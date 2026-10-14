import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

EMBED_DIM = 384  # all-MiniLM-L6-v2


class Patient(Base):
    __tablename__ = "patients"
    id: Mapped[str] = mapped_column(String(8), primary_key=True)  # P-001
    name: Mapped[str] = mapped_column(String(80))
    age: Mapped[int] = mapped_column(Integer)
    substance: Mapped[str] = mapped_column(String(80))
    summary: Mapped[str] = mapped_column(Text)
    timeline: Mapped[list] = mapped_column(JSON, default=list)
    synthetic: Mapped[bool] = mapped_column(default=True)


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    source_file: Mapped[str] = mapped_column(String(200), unique=True)
    chunks: Mapped[list["Chunk"]] = relationship(back_populates="document")


class Chunk(Base):
    __tablename__ = "chunks"
    id: Mapped[int] = mapped_column(primary_key=True)
    citation_id: Mapped[str] = mapped_column(String(40), unique=True)  # e.g. NIDA-p12-c3
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    section: Mapped[str | None] = mapped_column(String(200))
    page: Mapped[int | None]
    text: Mapped[str] = mapped_column(Text)
    embedding = mapped_column(Vector(EMBED_DIM))
    document: Mapped[Document] = relationship(back_populates="chunks")


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    correlation_id: Mapped[str] = mapped_column(String(36), default=lambda: str(uuid.uuid4()), index=True)
    user_email: Mapped[str | None] = mapped_column(String(200))
    event_type: Mapped[str] = mapped_column(String(60))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
