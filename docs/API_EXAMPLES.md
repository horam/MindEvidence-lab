# API examples

Base URL `http://localhost:8000`. Interactive docs: `/docs` (Swagger) and `/redoc`. Static spec: `docs/openapi.json`.
All patient data is synthetic. Lists return `{"items": [...], "total": N, "limit": L, "offset": O}` (`limit` 1-100, default 50).

    curl localhost:8000/api/health
    curl "localhost:8000/api/patients?limit=3&offset=0"
    curl localhost:8000/api/patients/P-001
    curl "localhost:8000/api/patients/P-001/history?limit=20"
    curl localhost:8000/api/papers

Sessions use the **development-only** identity header (not authentication; omit it to act as `dev-user`):

    curl -X POST localhost:8000/api/sessions -H "Content-Type: application/json" -H "X-Dev-User: alice" \
      -d '{"patient_id": "P-002", "mode": "rag", "title": "Cannabis case"}'
    curl -H "X-Dev-User: alice" localhost:8000/api/sessions
    curl -H "X-Dev-User: alice" localhost:8000/api/sessions/<session_id>/messages

Errors share one shape:

    GET /api/patients/P-999   -> 404 {"error": {"code": "patient_not_found", "message": "No patient with ID P-999", "details": null}}
    GET /api/patients/abc     -> 422 {"error": {"code": "validation_error", "message": "Request validation failed", "details": [{"field": "path.patient_id", "message": "..."}]}}
    GET /api/sessions/<someone else's id>/messages -> 404 session_not_found

Codes: `validation_error` (422), `patient_not_found` / `session_not_found` / `not_found` (404), `method_not_allowed` (405),
`auth_not_available` (503, sessions outside development), `internal_error` (500).
