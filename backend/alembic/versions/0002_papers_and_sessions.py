"""research.papers (metadata) and app.chat_sessions / app.chat_messages."""
from alembic import op

revision = "0002"
down_revision = "0001"


def upgrade():
    op.execute("""
    CREATE TABLE research.papers (
      paper_id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
      title            text NOT NULL UNIQUE,
      publisher        text NOT NULL,
      publication_year smallint CHECK (publication_year BETWEEN 1900 AND 2100),  -- NULL = not recorded
      source_file      text,
      ingestion_status text NOT NULL DEFAULT 'not_ingested' CHECK (ingestion_status IN ('not_ingested','ingested','failed')),
      created_at       timestamptz NOT NULL DEFAULT now()
    )""")
    op.execute("""
    CREATE TABLE app.chat_sessions (
      session_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      owner_id   text NOT NULL CHECK (owner_id ~ '^[A-Za-z0-9_.@-]{1,64}$'),  -- becomes a FK to app.users in Batch 04
      patient_id text REFERENCES patient_data.patients ON DELETE SET NULL,
      title      text CHECK (title IS NULL OR length(title) BETWEEN 1 AND 120),
      mode       text NOT NULL DEFAULT 'both' CHECK (mode IN ('general','rag','both','auto')),
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now()
    )""")
    op.execute("CREATE INDEX chat_sessions_owner_idx ON app.chat_sessions (owner_id, created_at DESC)")
    op.execute("""
    CREATE TABLE app.chat_messages (
      message_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
      session_id uuid NOT NULL REFERENCES app.chat_sessions ON DELETE CASCADE,
      role       text NOT NULL CHECK (role IN ('user','assistant','system')),
      content    text NOT NULL,
      created_at timestamptz NOT NULL DEFAULT now()
    )""")
    op.execute("CREATE INDEX chat_messages_session_idx ON app.chat_messages (session_id, message_id)")


def downgrade():
    op.execute("DROP TABLE app.chat_messages")
    op.execute("DROP TABLE app.chat_sessions")
    op.execute("DROP TABLE research.papers")
