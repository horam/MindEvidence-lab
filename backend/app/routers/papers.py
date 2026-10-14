from fastapi import APIRouter

from .. import services
from ..schemas import Page, PaperOut
from .deps import DB, ERR422, Pg

router = APIRouter(prefix="/papers", tags=["papers"])


@router.get("", response_model=Page[PaperOut], responses=ERR422, summary="List registered research papers (metadata only; ingestion is Batch 05)")
def list_papers(db: DB, pg: Pg):
    rows, total = services.paper_page(db, pg.limit, pg.offset)
    return pg.page(rows, total, PaperOut)
