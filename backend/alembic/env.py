from alembic import context
from sqlalchemy import create_engine

from app.config import settings

if context.is_offline_mode():
    raise SystemExit("Offline mode is not supported; run against a database.")
engine = create_engine(settings.sqlalchemy_url)
with engine.connect() as connection:
    context.configure(connection=connection)
    with context.begin_transaction():
        context.run_migrations()
