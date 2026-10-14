from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import errors
from .config import settings
from .routers import health, papers, patients, sessions

DESCRIPTION = """Backend for MindEvidence Lab, an educational tool. **All patient data is synthetic.**

**Access policy (development only):** there is no authentication yet. Session endpoints identify the caller by the
unverified `X-Dev-User` header and enforce ownership against it, but anyone can claim any identity. Do not treat these
endpoints as secure. They return 503 unless `APP_ENV=development`. Real sign-in arrives in Batch 04.

Errors always use `{"error": {"code", "message", "details"}}`. No RAG, LLM or OAuth features exist yet."""

app = FastAPI(title="MindEvidence Lab API", version="0.2.0", description=DESCRIPTION)
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], allow_credentials=False,
                   allow_methods=["GET", "POST"], allow_headers=["Content-Type", "X-Dev-User"])
errors.install(app)
for r in (health.router, patients.router, papers.router, sessions.router):
    app.include_router(r, prefix="/api")
