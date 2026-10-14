"""Usage (from backend/): python -m db.manage {migrate|seed|setup|reset --yes}
Credentials come only from the DATABASE_URL environment variable."""
import os, sys
from datetime import date
from pathlib import Path

import psycopg

from .seed_data import CASES, PAPERS, REFERENCE_DATE

HERE = Path(__file__).parent


def connect():
    url = os.environ.get("DATABASE_URL")
    if not url:
        sys.exit("DATABASE_URL is not set (see .env.example).")
    return psycopg.connect(url.replace("postgresql+psycopg://", "postgresql://"))


def parse(s):
    if s is None:
        return None, "unknown"
    p = [int(x) for x in s.split("-")]
    return date(p[0], p[1] if len(p) > 1 else 1, p[2] if len(p) > 2 else 1), {1: "year", 2: "month", 3: "day"}[len(p)]


def migrate(c=None):
    """Applies Alembic migrations to head (the c argument is accepted for backward compatibility)."""
    from alembic import command
    from alembic.config import Config
    cfg = Config(str(HERE.parent / "alembic.ini"))
    cfg.set_main_option("script_location", str(HERE.parent / "alembic"))
    command.upgrade(cfg, "head")


def seed(c):
    """Deterministic: wipes patient_data and papers (CASCADE also clears dev sessions), then reloads in one transaction."""
    c.execute("TRUNCATE patient_data.patients RESTART IDENTITY CASCADE")
    ref = parse(REFERENCE_DATE)[0]
    for k in CASES:
        pid = k["id"]
        c.execute("INSERT INTO patient_data.patients (patient_id, display_alias, age_years, gender_identity, primary_category,"
                  " motivation_stage, social_context, co_occurring_symptoms, summary, case_reference_date)"
                  " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                  (pid, k["alias"], k["age"], k["gender"], k["cat"], k["motiv"], k["social"], k["symptoms"], k["summary"], ref))
        for i, (d, t, text) in enumerate(k["events"], 1):
            dt, prec = parse(d)
            c.execute("INSERT INTO patient_data.patient_history_events (patient_id, event_seq, event_date, date_precision, event_type, description)"
                      " VALUES (%s,%s,%s,%s,%s,%s)", (pid, i, dt, prec, t, text))
        for name, prim, pat, freq, qty, s, e, st in k["uses"]:
            c.execute("INSERT INTO patient_data.substance_or_behavior_use (patient_id, name, category, is_primary, pattern, frequency_text,"
                      " quantity_text, start_date, end_date, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                      (pid, name, k["cat"], prim, pat, freq, qty, parse(s)[0], parse(e)[0], st))
        for kind, dom, text in k["risks"]:
            c.execute("INSERT INTO patient_data.triggers_and_risk_factors (patient_id, kind, domain, description) VALUES (%s,%s,%s,%s)", (pid, kind, dom, text))
        for typ, setting, s, e, st, note in k["interv"]:
            c.execute("INSERT INTO patient_data.previous_interventions (patient_id, intervention_type, setting, start_date, end_date, status, outcome_note)"
                      " VALUES (%s,%s,%s,%s,%s,%s,%s)", (pid, typ, setting, parse(s)[0], parse(e)[0], st, note))
        for d, dom, direction, text in k["prog"]:
            c.execute("INSERT INTO patient_data.progress_observations (patient_id, observed_on, domain, direction, observation) VALUES (%s,%s,%s,%s,%s)",
                      (pid, parse(d)[0], dom, direction, text))
    c.execute("TRUNCATE research.papers RESTART IDENTITY")
    for title, publisher, year in PAPERS:
        c.execute("INSERT INTO research.papers (title, publisher, publication_year) VALUES (%s,%s,%s)", (title, publisher, year))
    c.commit()


def reset(c):
    for s in ("patient_data", "research", "app", "audit"):
        c.execute(f"DROP SCHEMA IF EXISTS {s} CASCADE")
    c.execute("DROP TABLE IF EXISTS public.schema_migrations")
    c.execute("DROP TABLE IF EXISTS public.alembic_version")
    c.commit()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "reset" and "--yes" not in sys.argv:
        sys.exit("reset drops all app schemas; pass --yes to confirm.")
    with connect() as conn:
        {"migrate": migrate, "seed": seed, "reset": reset, "setup": lambda c: (migrate(c), seed(c))}.get(cmd, lambda c: sys.exit(__doc__))(conn)
    print("done:", cmd)
