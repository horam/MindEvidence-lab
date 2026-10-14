"""ORM mappings for tables created by the Alembic migrations (schemas: patient_data, research, app)."""
import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, SmallInteger, String, Text, Uuid, func, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

PD = {"schema": "patient_data"}
def FK_PATIENT():
    return ForeignKey("patient_data.patients.patient_id")


class Patient(Base):
    __tablename__, __table_args__ = "patients", PD
    patient_id: Mapped[str] = mapped_column(String, primary_key=True)
    display_alias: Mapped[str]
    age_years: Mapped[int] = mapped_column(SmallInteger)
    gender_identity: Mapped[str]
    primary_category: Mapped[str]
    motivation_stage: Mapped[str]
    social_context: Mapped[str]
    co_occurring_symptoms: Mapped[list[str]] = mapped_column(ARRAY(Text))
    summary: Mapped[str]
    case_reference_date: Mapped[date] = mapped_column(Date)
    is_synthetic: Mapped[bool]
    synthetic_notice: Mapped[str]
    use: Mapped[list["UseRow"]] = relationship(order_by="UseRow.start_date")
    factors: Mapped[list["Factor"]] = relationship(order_by="Factor.factor_id")
    interventions: Mapped[list["Intervention"]] = relationship(order_by="Intervention.start_date")
    progress: Mapped[list["Progress"]] = relationship(order_by="Progress.observed_on")


class HistoryEvent(Base):
    __tablename__, __table_args__ = "patient_history_events", PD
    event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    patient_id: Mapped[str] = mapped_column(FK_PATIENT())
    event_seq: Mapped[int] = mapped_column(Integer)
    event_date: Mapped[date | None] = mapped_column(Date)
    date_precision: Mapped[str]
    event_type: Mapped[str]
    description: Mapped[str]


class UseRow(Base):
    __tablename__, __table_args__ = "substance_or_behavior_use", PD
    use_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    patient_id: Mapped[str] = mapped_column(FK_PATIENT())
    name: Mapped[str]
    category: Mapped[str]
    is_primary: Mapped[bool]
    pattern: Mapped[str]
    frequency_text: Mapped[str]
    quantity_text: Mapped[str]
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str]


class Factor(Base):
    __tablename__, __table_args__ = "triggers_and_risk_factors", PD
    factor_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    patient_id: Mapped[str] = mapped_column(FK_PATIENT())
    kind: Mapped[str]
    domain: Mapped[str]
    description: Mapped[str]


class Intervention(Base):
    __tablename__, __table_args__ = "previous_interventions", PD
    intervention_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    patient_id: Mapped[str] = mapped_column(FK_PATIENT())
    intervention_type: Mapped[str]
    setting: Mapped[str]
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str]
    outcome_note: Mapped[str]


class Progress(Base):
    __tablename__, __table_args__ = "progress_observations", PD
    observation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    patient_id: Mapped[str] = mapped_column(FK_PATIENT())
    observed_on: Mapped[date] = mapped_column(Date)
    domain: Mapped[str]
    direction: Mapped[str]
    observation: Mapped[str]


class Paper(Base):
    __tablename__, __table_args__ = "papers", {"schema": "research"}
    paper_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str]
    publisher: Mapped[str]
    publication_year: Mapped[int | None] = mapped_column(SmallInteger)
    source_file: Mapped[str | None]
    ingestion_status: Mapped[str]


class ChatSession(Base):
    __tablename__, __table_args__ = "chat_sessions", {"schema": "app"}
    session_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text("gen_random_uuid()"))
    owner_id: Mapped[str]                       # development identity until users exist (Batch 04)
    patient_id: Mapped[str | None] = mapped_column(ForeignKey("patient_data.patients.patient_id", ondelete="SET NULL"))
    title: Mapped[str | None]
    mode: Mapped[str] = mapped_column(String, default="both")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ChatMessage(Base):
    __tablename__, __table_args__ = "chat_messages", {"schema": "app"}
    message_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("app.chat_sessions.session_id", ondelete="CASCADE"))
    role: Mapped[str]
    content: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
