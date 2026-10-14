from typing import Annotated

from fastapi import Depends, Path, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import ErrorResponse, Page

DB = Annotated[Session, Depends(get_db)]
PatientId = Annotated[str, Path(pattern=r"^P-\d{3}$", description="Synthetic patient ID, P-001 to P-010", examples=["P-001"])]
ERRORS = {404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}}
ERR422 = {422: {"model": ErrorResponse}}


class Pagination:
    def __init__(self, limit: int = Query(50, ge=1, le=100, description="Page size"),
                 offset: int = Query(0, ge=0, le=100_000, description="Rows to skip")):
        self.limit, self.offset = limit, offset

    def page(self, items, total, model):
        return Page[model](items=[model.model_validate(i) for i in items], total=total, limit=self.limit, offset=self.offset)


Pg = Annotated[Pagination, Depends()]
