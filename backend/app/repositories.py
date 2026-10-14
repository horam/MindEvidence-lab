"""Database access only: queries in, ORM rows out. No HTTP and no business rules here."""
import uuid

from sqlalchemy import BigInteger, func, literal_column, select, union_all
from sqlalchemy.orm import Session, selectinload

from . import models as m


def list_patients(db: Session, limit: int, offset: int):
    total = db.scalar(select(func.count()).select_from(m.Patient))
    rows = db.scalars(select(m.Patient).order_by(m.Patient.patient_id).limit(limit).offset(offset)).all()
    return rows, total


def get_patient(db: Session, pid: str):
    opts = [selectinload(m.Patient.use), selectinload(m.Patient.factors), selectinload(m.Patient.interventions), selectinload(m.Patient.progress)]
    return db.scalar(select(m.Patient).where(m.Patient.patient_id == pid).options(*opts))


def patient_exists(db: Session, pid: str) -> bool:
    return db.scalar(select(m.Patient.patient_id).where(m.Patient.patient_id == pid)) is not None


def timeline(db: Session, pid: str, limit: int, offset: int):
    h, o = m.HistoryEvent, m.Progress
    ev = select(h.event_date.label("event_date"), h.date_precision.label("date_precision"), literal_column("'history'").label("source"),
                h.event_type.label("event_type"), h.description.label("description"), literal_column("0").label("ord"),
                h.event_seq.cast(BigInteger).label("seq")).where(h.patient_id == pid)
    ob = select(o.observed_on, literal_column("'day'"), literal_column("'progress'"),
                func.concat(literal_column("'observation:'"), o.domain, literal_column("':'"), o.direction),
                o.observation, literal_column("1"), o.observation_id).where(o.patient_id == pid)
    u = union_all(ev, ob).subquery()
    total = db.scalar(select(func.count()).select_from(u))
    rows = db.execute(select(u.c.event_date, u.c.date_precision, u.c.source, u.c.event_type, u.c.description)
                      .order_by(u.c.event_date.asc().nulls_last(), u.c.ord, u.c.seq).limit(limit).offset(offset)).mappings().all()
    return rows, total


def list_papers(db: Session, limit: int, offset: int):
    total = db.scalar(select(func.count()).select_from(m.Paper))
    return db.scalars(select(m.Paper).order_by(m.Paper.paper_id).limit(limit).offset(offset)).all(), total


def create_session(db: Session, owner: str, patient_id, title, mode):
    s = m.ChatSession(owner_id=owner, patient_id=patient_id, title=title, mode=mode)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def list_sessions(db: Session, owner: str, patient_id, limit: int, offset: int):
    q = select(m.ChatSession).where(m.ChatSession.owner_id == owner)
    if patient_id:
        q = q.where(m.ChatSession.patient_id == patient_id)
    total = db.scalar(select(func.count()).select_from(q.subquery()))
    rows = db.scalars(q.order_by(m.ChatSession.created_at.desc(), m.ChatSession.session_id).limit(limit).offset(offset)).all()
    return rows, total


def get_owned_session(db: Session, owner: str, sid: uuid.UUID):
    return db.scalar(select(m.ChatSession).where(m.ChatSession.session_id == sid, m.ChatSession.owner_id == owner))


def list_messages(db: Session, sid: uuid.UUID, limit: int, offset: int):
    q = select(m.ChatMessage).where(m.ChatMessage.session_id == sid)
    total = db.scalar(select(func.count()).select_from(q.subquery()))
    return db.scalars(q.order_by(m.ChatMessage.message_id).limit(limit).offset(offset)).all(), total
