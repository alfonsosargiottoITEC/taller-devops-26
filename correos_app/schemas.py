"""Pydantic schemas."""

from pydantic import BaseModel


class EmailPayload(BaseModel):
    destinatario: str
    asunto: str
    mensaje: str


class SentEmail(BaseModel):
    id: int
    destinatario: str
    asunto: str
    mensaje: str
    created_at: str
