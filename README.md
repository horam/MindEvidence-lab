# MindEvidence Lab

Educational RAG research assistant for addiction-treatment students. Teaching tool only: it does not diagnose, prescribe, or choose treatments. All patients are synthetic. See `docs/SPEC.md`.

## Status
| Batch | Status |
|---|---|
| 01 Frontend with mock data | Done (see frontend/README.md) |
| 02 PostgreSQL data model and seed | Done: SQL migrations, seed, tests (see below) |
| 03 FastAPI backend | Done: 8 endpoints, Alembic, tests; frontend patient list/detail use the API |
| 04-10 | Not started (DeepSeek provider interface is stubbed) |

Nothing here is production-ready or clinically validated.

## Run
Frontend (no build step):

    cd frontend && python -m http.server 5500

Backend:

    docker compose up -d db
    cd backend && python -m venv .venv && . .venv/bin/activate
    pip install -r requirements.txt
    cp ../.env.example ../.env
    uvicorn app.main:app --reload

## Database (Batch 02)
Plain SQL migrations in `backend/db/migrations/`, seed data in `backend/db/seed_data.py`, sample queries in `backend/db/queries/`.
Docs: `docs/DATA_DICTIONARY.md`, `docs/FRONTEND_INTEGRATION_PLAN.md`. The patient tables live in schema `patient_data` and are all synthetic.

    export DATABASE_URL=postgresql://mind:mind@localhost:5432/mindevidence   # credentials only via environment
    cd backend
    python -m db.manage setup              # migrate + seed (repeatable)
    python -m db.manage reset --yes        # drops app schemas (destructive)
    python -m pytest                        # run on a throwaway database only

Note: `backend/app/models.py` (SQLAlchemy, drafted earlier) does not yet match these tables; the SQL migrations are authoritative until Batch 03 reconciles them.

## Backend API (Batch 03)
FastAPI + SQLAlchemy 2 + Alembic + Pydantic v2. Layers: `routers/` (HTTP) -> `services.py` (rules) -> `repositories.py` (SQL) with `models.py`, `schemas.py`, `errors.py`, `access.py`.
Examples: `docs/API_EXAMPLES.md`. OpenAPI: `/docs`, `/openapi.json`, or `docs/openapi.json`.

    cp .env.example .env                      # set DATABASE_URL, APP_ENV=development, FRONTEND_ORIGIN=http://localhost:5500
    docker compose up -d db
    cd backend && pip install -r requirements.txt
    set -a; . ../.env; set +a                 # DATABASE_URL from the environment
    python -m db.manage reset --yes           # only if you ran the Batch 02 SQL runner before (Alembic replaces it)
    python -m db.manage setup                 # alembic upgrade head + seed
    uvicorn app.main:app --reload             # http://localhost:8000/docs
    (cd ../frontend && python -m http.server 5500)
    python -m pytest                          # throwaway database only: tests reseed it

Alembic: `alembic upgrade head` also works from `backend/`. Revision 0001 applies the Batch 02 SQL files (single source of truth); 0002 adds `research.papers`, `app.chat_sessions`, `app.chat_messages`.
Reseeding truncates patients with CASCADE, which also clears development sessions.

**Security status:** no authentication exists. Session endpoints use the unverified `X-Dev-User` header as a development-only policy, with ownership checks that will carry over to real identities in Batch 04, and return 503 unless `APP_ENV=development`. CORS allows only `FRONTEND_ORIGIN` (GET/POST, no credentials). Not production-ready.
