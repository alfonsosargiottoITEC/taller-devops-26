"""Application settings."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    app_env: str
    secret_key: str
    log_level: str
    port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    db_host: str
    db_port: int
    database_url: str
    sqlite_path: Path
    database_connect_timeout: float

    @property
    def resolved_database_url(self) -> str:
        if self.database_url and "${" not in self.database_url:
            return self.database_url

        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.db_host}:{self.db_port}/{self.postgres_db}"
        )


def get_settings() -> Settings:
    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        secret_key=os.getenv("SECRET_KEY", "change-me"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        port=int(os.getenv("PORT", "8000")),
        postgres_user=os.getenv("POSTGRES_USER", "postgres"),
        postgres_password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        postgres_db=os.getenv("POSTGRES_DB", "correos_db"),
        db_host=os.getenv("DB_HOST", os.getenv("POSTGRES_HOST", "db")),
        db_port=int(os.getenv("DB_PORT", os.getenv("POSTGRES_PORT", "5432"))),
        database_url=os.getenv("DATABASE_URL", "").strip(),
        sqlite_path=Path(os.getenv("SQLITE_PATH", "/tmp/app-correos.sqlite3")),
        database_connect_timeout=float(os.getenv("DATABASE_CONNECT_TIMEOUT", "2")),
    )
