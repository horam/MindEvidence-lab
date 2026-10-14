"""Pydantic v2 request/response models (these appear in the OpenAPI spec)."""
import uuid
from datetime import date, datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")
Category = Literal["alcohol", "cannabis", "opioid", "stimulant", "behavioral"]
Mode = Literal["general", "rag", "both", "auto"]


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(description="Total rows matching the query, ignoring limit/offset")
    limit: int
    offset: int


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str


class ErrorBody(BaseModel):
    code: str = Field(examples=["patient_not_found"])
    message: str
    details: list[ErrorDetail] | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody


class HealthOut(BaseModel):
    status: Literal["ok", "degraded"]
    database: Literal["ok", "unavailable"]
    version: str


class PatientSummary(ORM):
    patient_id: str
    display_alias: str
    age_years: int
    primary_category: Category
    motivation_stage: str
    summary: str
    is_synthetic: bool
    synthetic_notice: str


class UseOut(ORM):
    name: str
    category: Category
    is_primary: bool
    pattern: str
    frequency_text: str
    quantity_text: str
    start_date: date
    end_date: date | None
    status: str


class FactorOut(ORM):
    kind: Literal["trigger", "risk_factor", "protective_factor", "observed_behavior"]
    domain: str
    description: str


class InterventionOut(ORM):
    intervention_type: str
    setting: str
    start_date: date
    end_date: date | None
    status: str
    outcome_note: str


class ProgressOut(ORM):
    observed_on: date
    domain: str
    direction: str
    observation: str


class PatientDetail(PatientSummary):
    gender_identity: str
    social_context: str
    co_occurring_symptoms: list[str]
    case_reference_date: date
    use: list[UseOut]
    factors: list[FactorOut]
    interventions: list[InterventionOut]
    progress: list[ProgressOut]


class HistoryItem(BaseModel):
    event_date: date | None = Field(description="Null only when date_precision is 'unknown'")
    date_precision: Literal["year", "month", "day", "unknown"]
    source: Literal["history", "progress"]
    event_type: str
    description: str


class PaperOut(ORM):
    paper_id: int
    title: str
    publisher: str
    publication_year: int | None
    ingestion_status: Literal["not_ingested", "ingested", "failed"]


class SessionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    patient_id: str | None = Field(default=None, pattern=r"^P-\d{3}$", examples=["P-001"])
    mode: Mode = "both"
    title: str | None = Field(default=None, min_length=1, max_length=120)


class SessionOut(ORM):
    session_id: uuid.UUID
    patient_id: str | None
    title: str | None
    mode: Mode
    created_at: datetime
    updated_at: datetime


class MessageOut(ORM):
    message_id: int
    session_id: uuid.UUID
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime
