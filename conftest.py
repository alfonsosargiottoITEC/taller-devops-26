"""Shared pytest helpers for the app."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

import pytest
from starlette.requests import Request

from app import app


@dataclass
class FakeEmail:
    id: int
    destinatario: str
    asunto: str
    mensaje: str
    created_at: str

    def model_dump(self) -> dict[str, str | int]:
        return {
            "id": self.id,
            "destinatario": self.destinatario,
            "asunto": self.asunto,
            "mensaje": self.mensaje,
            "created_at": self.created_at,
        }


class FakeEmailStore:
    def __init__(self, emails: list[FakeEmail] | None = None):
        self._emails = list(emails or [])
        self.ready = True
        self.error = None

    def bootstrap(self) -> None:
        self.ready = True

    def ensure_ready(self) -> None:
        return None

    def list_emails(self) -> list[FakeEmail]:
        return list(self._emails)

    def save(self, payload) -> dict[str, str | int]:
        email = FakeEmail(
            id=len(self._emails) + 1,
            destinatario=payload.destinatario,
            asunto=payload.asunto,
            mensaje=payload.mensaje,
            created_at="2026-08-17T10:00:00",
        )
        self._emails.insert(0, email)
        return {"id": email.id, "created_at": email.created_at}

    def health(self) -> dict[str, str]:
        return {"database": "ready", "backend": "sqlite"}


def make_request(
    path: str = "/",
    method: str = "GET",
    body: bytes = b"",
    headers: dict[str, str] | None = None,
) -> Request:
    raw_headers = [
        (name.lower().encode("latin-1"), value.encode("latin-1"))
        for name, value in (headers or {}).items()
    ]
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "query_string": b"",
        "headers": raw_headers,
        "app": app,
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
        "scheme": "http",
        "http_version": "1.1",
    }

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    return Request(scope, receive)


@pytest.fixture
def store_factory() -> Iterator:
    original_store = app.state.email_store

    def factory(emails: list[FakeEmail] | None = None) -> FakeEmailStore:
        store = FakeEmailStore(emails)
        app.state.email_store = store
        return store

    yield factory
    app.state.email_store = original_store
