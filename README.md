# MindEvidence Lab

Educational RAG research assistant for addiction-treatment students. Teaching tool only: it does not diagnose, prescribe, or choose treatments. All patients are synthetic. See `docs/SPEC.md`.

## Status
| Batch | Status |
|---|---|
| 01 Frontend with mock data | Done (mock answers, clearly labeled) |
| 02 Data model | Models drafted in `backend/app/models.py`; Alembic and seed not yet |
| 03 FastAPI backend | Skeleton: health, patients and chat stubs (501) |
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
