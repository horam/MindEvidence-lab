"""Business rules: existence checks, ownership checks, error mapping. No SQL and no HTTP details."""
import uuid

from sqlalchemy.orm import Session

from . import repositories as repo
from .errors import ApiError


def _no_patient(pid):
    return ApiError(404, "patient_not_found", f"No patient with ID {pid}")


def patient_page(db: Session, limit: int, offset: int):
    return repo.list_patients(db, limit, offset)


def patient_detail(db: Session, pid: str):
    p = repo.get_patient(db, pid)
    if p is None:
        raise _no_patient(pid)
    return p


def patient_history(db: Session, pid: str, limit: int, offset: int):
    if not repo.patient_exists(db, pid):
        raise _no_patient(pid)
    return repo.timeline(db, pid, limit, offset)


def paper_page(db: Session, limit: int, offset: int):
    return repo.list_papers(db, limit, offset)


def open_session(db: Session, owner: str, patient_id, title, mode):
    if patient_id is not None and not repo.patient_exists(db, patient_id):
        raise _no_patient(patient_id)
    return repo.create_session(db, owner, patient_id, title, mode)


def owned_sessions(db: Session, owner: str, patient_id, limit: int, offset: int):
    return repo.list_sessions(db, owner, patient_id, limit, offset)


def session_messages(db: Session, owner: str, sid: uuid.UUID, limit: int, offset: int):
    # Ownership check. A session owned by someone else looks exactly like a missing one.
    if repo.get_owned_session(db, owner, sid) is None:
        raise ApiError(404, "session_not_found", "Session not found")
    return repo.list_messages(db, sid, limit, offset)
