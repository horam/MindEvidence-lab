import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from .. import services
from ..access import dev_owner
from ..errors import ApiError  # noqa: F401
from ..schemas import MessageOut, Page, SessionCreate, SessionOut
from .deps import DB, ERR422, ERRORS, Pg

Owner = Annotated[str, Depends(dev_owner)]
router = APIRouter(prefix="/sessions", tags=["sessions (development-only access policy)"],
                   responses={503: {"description": "Disabled outside APP_ENV=development until authentication exists"}})


@router.get("", response_model=Page[SessionOut], responses=ERR422, summary="List the caller's sessions")
def list_sessions(owner: Owner, db: DB, pg: Pg, patient_id: Annotated[str | None, Query(pattern=r"^P-\d{3}$")] = None):
    rows, total = services.owned_sessions(db, owner, patient_id, pg.limit, pg.offset)
    return pg.page(rows, total, SessionOut)


@router.post("", response_model=SessionOut, status_code=201, responses=ERRORS, summary="Create a session")
def create_session(body: SessionCreate, owner: Owner, db: DB):
    return SessionOut.model_validate(services.open_session(db, owner, body.patient_id, body.title, body.mode))


@router.get("/{session_id}/messages", response_model=Page[MessageOut], responses=ERRORS, summary="List messages of an owned session")
def list_messages(session_id: uuid.UUID, owner: Owner, db: DB, pg: Pg):
    rows, total = services.session_messages(db, owner, session_id, pg.limit, pg.offset)
    return pg.page(rows, total, MessageOut)
