"""Integrity and consistency tests. Run against a THROWAWAY database: DATABASE_URL=... python -m pytest"""
import os
import pytest
import psycopg
from db import manage

pytestmark = pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL not set")
PD = "patient_data."
CHILDREN = ["patient_history_events", "substance_or_behavior_use", "triggers_and_risk_factors", "previous_interventions", "progress_observations"]


@pytest.fixture(scope="module")
def c():
    conn = manage.connect()
    manage.migrate(conn)
    manage.seed(conn)
    yield conn
    conn.rollback()
    conn.close()


def rows(c, sql, *a):
    with c.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall()


def test_ten_stable_synthetic_patients(c):
    assert [r[0] for r in rows(c, f"SELECT patient_id FROM {PD}patients ORDER BY 1")] == [f"P-{i:03d}" for i in range(1, 11)]
    assert rows(c, f"SELECT count(*) FROM {PD}patients WHERE NOT is_synthetic")[0][0] == 0


@pytest.mark.parametrize("t", CHILDREN)
def test_no_orphans_and_all_synthetic(c, t):
    assert rows(c, f"SELECT count(*) FROM {PD}{t} x LEFT JOIN {PD}patients p USING (patient_id) WHERE p.patient_id IS NULL")[0][0] == 0
    assert rows(c, f"SELECT count(*) FROM {PD}{t} WHERE NOT is_synthetic")[0][0] == 0


def test_every_patient_has_core_records(c):
    bad = rows(c, f"""SELECT p.patient_id FROM {PD}patients p WHERE
      (SELECT count(*) FROM {PD}patient_history_events WHERE patient_id=p.patient_id) < 3 OR
      (SELECT count(*) FROM {PD}substance_or_behavior_use WHERE patient_id=p.patient_id AND is_primary) <> 1 OR
      (SELECT count(*) FROM {PD}triggers_and_risk_factors WHERE patient_id=p.patient_id) < 3 OR
      (SELECT count(*) FROM {PD}progress_observations WHERE patient_id=p.patient_id) < 2""")
    assert bad == []


def test_variety(c):
    assert {r[0] for r in rows(c, f"SELECT primary_category FROM {PD}patients")} == {"alcohol", "cannabis", "opioid", "stimulant", "behavioral"}
    assert rows(c, f"SELECT count(DISTINCT motivation_stage) FROM {PD}patients")[0][0] >= 4
    # same category, different situations (no category-determines-treatment shortcut)
    assert rows(c, f"SELECT count(DISTINCT motivation_stage) FROM {PD}patients WHERE primary_category='alcohol'")[0][0] >= 2


def test_dates_in_order_and_not_in_future(c):
    assert rows(c, f"""SELECT 1 FROM (SELECT h.*, lag(event_date) OVER (PARTITION BY patient_id ORDER BY event_seq) prev
      FROM {PD}patient_history_events h) x WHERE prev > event_date""") == []
    assert rows(c, f"SELECT 1 FROM {PD}patient_history_events h JOIN {PD}patients p USING (patient_id) WHERE h.event_date > p.case_reference_date") == []
    assert rows(c, f"""SELECT 1 FROM {PD}progress_observations o JOIN {PD}patients p USING (patient_id) WHERE o.observed_on > p.case_reference_date
      OR o.observed_on < (SELECT min(event_date) FROM {PD}patient_history_events WHERE patient_id=o.patient_id)""") == []


def test_primary_use_matches_onset_event(c):
    assert rows(c, f"""SELECT u.patient_id FROM {PD}substance_or_behavior_use u WHERE is_primary AND NOT EXISTS
      (SELECT 1 FROM {PD}patient_history_events h WHERE h.patient_id=u.patient_id AND h.event_type='onset' AND h.event_date=u.start_date)""") == []
    assert rows(c, f"SELECT 1 FROM {PD}substance_or_behavior_use u JOIN {PD}patients p USING (patient_id) WHERE u.category <> p.primary_category") == []


def test_interventions_and_events_agree(c):
    assert rows(c, f"""SELECT i.patient_id FROM {PD}previous_interventions i WHERE NOT EXISTS (SELECT 1 FROM {PD}patient_history_events h
      WHERE h.patient_id=i.patient_id AND h.event_type='intervention_start' AND h.event_date=i.start_date)""") == []
    assert rows(c, f"""SELECT i.patient_id FROM {PD}previous_interventions i WHERE i.end_date IS NOT NULL AND NOT EXISTS (SELECT 1 FROM {PD}patient_history_events h
      WHERE h.patient_id=i.patient_id AND h.event_type='intervention_end' AND h.event_date=i.end_date)""") == []
    assert rows(c, f"""SELECT h.patient_id FROM {PD}patient_history_events h WHERE h.event_type='intervention_start' AND NOT EXISTS (SELECT 1 FROM {PD}previous_interventions i
      WHERE i.patient_id=h.patient_id AND i.start_date=h.event_date)""") == []
    assert rows(c, f"""SELECT 1 FROM {PD}previous_interventions i JOIN {PD}substance_or_behavior_use u ON u.patient_id=i.patient_id AND u.is_primary
      WHERE i.start_date < u.start_date""") == []


def test_abstinence_and_relapse_logic(c):
    assert rows(c, f"""SELECT u.patient_id FROM {PD}substance_or_behavior_use u WHERE u.status='abstinent' AND u.end_date IS DISTINCT FROM
      (SELECT event_date FROM {PD}patient_history_events h WHERE h.patient_id=u.patient_id AND event_type IN ('abstinence_start','relapse') ORDER BY event_seq DESC LIMIT 1)""") == []
    assert rows(c, f"""SELECT h.patient_id FROM {PD}patient_history_events h WHERE event_type='relapse' AND NOT EXISTS (SELECT 1 FROM {PD}patient_history_events a
      WHERE a.patient_id=h.patient_id AND a.event_type='abstinence_start' AND a.event_seq < h.event_seq)""") == []


def test_no_contact_info(c):
    sql = " UNION ALL ".join([f"SELECT description FROM {PD}patient_history_events", f"SELECT description FROM {PD}triggers_and_risk_factors",
                              f"SELECT observation FROM {PD}progress_observations", f"SELECT summary FROM {PD}patients", f"SELECT social_context FROM {PD}patients"])
    assert rows(c, f"SELECT count(*) FROM ({sql}) t(x) WHERE x ~ '@|[0-9]{{3}}[-. ][0-9]{{3,4}}[-. ][0-9]{{4}}|https?:'")[0][0] == 0


@pytest.mark.parametrize("sql", [
    f"INSERT INTO {PD}patients (patient_id,display_alias,age_years,primary_category,social_context,summary,case_reference_date,is_synthetic) VALUES ('P-011','x',30,'alcohol','x','x','2025-09-01',false)",
    f"INSERT INTO {PD}patients (patient_id,display_alias,age_years,primary_category,social_context,summary,case_reference_date) VALUES ('X1','x',30,'alcohol','x','x','2025-09-01')",
    f"INSERT INTO {PD}patients (patient_id,display_alias,age_years,primary_category,social_context,summary,case_reference_date) VALUES ('P-012','x',15,'alcohol','x','x','2025-09-01')",
    f"INSERT INTO {PD}progress_observations (patient_id,observed_on,domain,direction,observation) VALUES ('P-999','2025-01-01','use','stable','x')",
])
def test_constraints_reject_bad_rows(c, sql):
    with pytest.raises(psycopg.errors.IntegrityError):
        c.execute(sql)
    c.rollback()


def test_query_functions(c):
    prof = rows(c, f"SELECT {PD}get_patient_profile('P-001')")[0][0]
    assert prof["patient_id"] == "P-001" and prof["is_synthetic"] and prof["use"] and prof["interventions"]
    tl = rows(c, f"SELECT * FROM {PD}patient_timeline('P-001')")
    n = rows(c, f"SELECT (SELECT count(*) FROM {PD}patient_history_events WHERE patient_id='P-001') + (SELECT count(*) FROM {PD}progress_observations WHERE patient_id='P-001')")[0][0]
    assert len(tl) == n and [r[0] for r in tl] == sorted(r[0] for r in tl)


def test_seed_is_reproducible(c):
    before = rows(c, f"SELECT {PD}get_patient_profile(patient_id) FROM {PD}patients ORDER BY 1")
    manage.seed(c)
    assert rows(c, f"SELECT {PD}get_patient_profile(patient_id) FROM {PD}patients ORDER BY 1") == before
