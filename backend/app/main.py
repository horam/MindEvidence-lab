from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import settings

app = FastAPI(title="MindEvidence Lab", version="0.1.0")
app.add_middleware(
    CORSMiddleware, allow_origins=[settings.frontend_origin],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)


class ChatRequest(BaseModel):
    patient_id: str = Field(pattern=r"^P-\d{3}$")
    question: str = Field(min_length=1, max_length=2000)
    mode: Literal["general", "rag", "both", "auto"] = "both"


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/patients")
def patients():
    # Batches 02-03: replace with a query against the seeded `patients` table.
    raise HTTPException(501, "Patients come from frontend mock data until batch 02 seeds the database.")


@app.post("/api/chat")
def chat(req: ChatRequest):
    # Batches 06-08: pgvector retrieval -> DeepSeek -> LangGraph, with audit events.
    raise HTTPException(501, "Chat pipeline not implemented yet (batches 06-08).")
