from fastapi import APIRouter

from .. import services
from ..schemas import HistoryItem, Page, PatientDetail, PatientSummary
from .deps import DB, ERR422, ERRORS, PatientId, Pg

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=Page[PatientSummary], responses=ERR422, summary="List synthetic patients")
def list_patients(db: DB, pg: Pg):
    rows, total = services.patient_page(db, pg.limit, pg.offset)
    return pg.page(rows, total, PatientSummary)


@router.get("/{patient_id}", response_model=PatientDetail, responses=ERRORS, summary="Full synthetic patient profile")
def get_patient(patient_id: PatientId, db: DB):
    return services.patient_detail(db, patient_id)


@router.get("/{patient_id}/history", response_model=Page[HistoryItem], responses=ERRORS,
            summary="Chronological history (events plus progress observations)")
def get_history(patient_id: PatientId, db: DB, pg: Pg):
    rows, total = services.patient_history(db, patient_id, pg.limit, pg.offset)
    return Page[HistoryItem](items=[HistoryItem(**r) for r in rows], total=total, limit=pg.limit, offset=pg.offset)
