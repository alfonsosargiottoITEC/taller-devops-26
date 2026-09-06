"""Persistence layer for sent emails."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any

from .config import Settings
from .schemas import EmailPayload, SentEmail

try:
    import psycopg
except ImportError:  # pragma: no cover - only happens outside Docker
    psycopg = None

logger = logging.getLogger(__name__)

CREATE_EMAILS_TABLE_POSTGRES = """
CREATE TABLE IF NOT EXISTS sent_emails (
    id BIGSERIAL PRIMARY KEY,
    destinatario TEXT NOT NULL,
    asunto TEXT NOT NULL,
    mensaje TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""

CREATE_EMAILS_TABLE_SQLITE = """
CREATE TABLE IF NOT EXISTS sent_emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destinatario TEXT NOT NULL,
    asunto TEXT NOT NULL,
    mensaje TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

INSERT_EMAIL_POSTGRES = """
INSERT INTO sent_emails (destinatario, asunto, mensaje)
VALUES (%s, %s, %s)
RETURNING id, created_at
"""

INSERT_EMAIL_SQLITE = """
INSERT INTO sent_emails (destinatario, asunto, mensaje)
VALUES (?, ?, ?)
"""

SELECT_EMAILS_POSTGRES = """
SELECT id, destinatario, asunto, mensaje, created_at
FROM sent_emails
ORDER BY id DESC
"""

SELECT_EMAILS_SQLITE = """
SELECT id, destinatario, asunto, mensaje, created_at
FROM sent_emails
ORDER BY id DESC
"""


class EmailStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.backend = "postgres" if psycopg is not None else "sqlite"
        self.ready = False
        self.error: str | None = None

    def bootstrap(self) -> None:
        try:
            if self.backend == "postgres":
                with self._postgres_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(CREATE_EMAILS_TABLE_POSTGRES)
                    conn.commit()
            else:
                with self._sqlite_connection() as conn:
                    conn.execute(CREATE_EMAILS_TABLE_SQLITE)
                    conn.commit()

            self.ready = True
            self.error = None
        except Exception as exc:  # pragma: no cover - depends on external DB state
            self.ready = False
            self.error = str(exc)
            logger.warning("No se pudo inicializar la persistencia: %s", exc)

    def ensure_ready(self) -> None:
        if not self.ready:
            self.bootstrap()
        if not self.ready:
            raise RuntimeError(self.error or "base de datos no disponible")

    def save(self, payload: EmailPayload) -> dict[str, Any]:
        if self.backend == "postgres":
            with self._postgres_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        INSERT_EMAIL_POSTGRES,
                        (payload.destinatario, payload.asunto, payload.mensaje),
                    )
                    row = cursor.fetchone()
                conn.commit()
                return {
                    "id": row[0],
                    "created_at": row[1].isoformat()
                    if hasattr(row[1], "isoformat")
                    else row[1],
                }

        with self._sqlite_connection() as conn:
            conn.row_factory = sqlite3.Row
            conn.execute(CREATE_EMAILS_TABLE_SQLITE)
            cursor = conn.execute(
                INSERT_EMAIL_SQLITE,
                (payload.destinatario, payload.asunto, payload.mensaje),
            )
            conn.commit()
            row = conn.execute(
                "SELECT id, created_at FROM sent_emails WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
            return {"id": row["id"], "created_at": row["created_at"]}

    def list_emails(self) -> list[SentEmail]:
        if self.backend == "postgres":
            with self._postgres_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(SELECT_EMAILS_POSTGRES)
                    rows = cursor.fetchall()
            return [
                SentEmail(
                    id=row[0],
                    destinatario=row[1],
                    asunto=row[2],
                    mensaje=row[3],
                    created_at=row[4].isoformat()
                    if hasattr(row[4], "isoformat")
                    else str(row[4]),
                )
                for row in rows
            ]

        with self._sqlite_connection() as conn:
            conn.row_factory = sqlite3.Row
            conn.execute(CREATE_EMAILS_TABLE_SQLITE)
            rows = conn.execute(SELECT_EMAILS_SQLITE).fetchall()
            return [
                SentEmail(
                    id=row["id"],
                    destinatario=row["destinatario"],
                    asunto=row["asunto"],
                    mensaje=row["mensaje"],
                    created_at=row["created_at"],
                )
                for row in rows
            ]

    def health(self) -> dict[str, str]:
        return {
            "database": "ready" if self.ready else "degraded",
            "backend": self.backend,
        }

    def _postgres_connection(self):
        return psycopg.connect(
            self.settings.resolved_database_url,
            connect_timeout=self.settings.database_connect_timeout,
        )

    def _sqlite_connection(self):
        path = Path(self.settings.sqlite_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(path)
