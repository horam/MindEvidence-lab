"""Batch 02 schema: applies the reviewed SQL files in db/migrations/ (single source of truth)."""
from pathlib import Path

from alembic import op

revision = "0001"
down_revision = None
SQL_DIR = Path(__file__).resolve().parents[2] / "db" / "migrations"


def upgrade():
    raw = op.get_bind().connection.driver_connection  # same transaction; plain execute allows multi-statement SQL
    for f in sorted(SQL_DIR.glob("*.sql")):
        raw.execute(f.read_text())


def downgrade():
    for s in ("patient_data", "research", "app", "audit"):
        op.execute(f"DROP SCHEMA IF EXISTS {s} CASCADE")
