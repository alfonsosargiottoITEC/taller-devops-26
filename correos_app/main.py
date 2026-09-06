"""Application factory."""

from __future__ import annotations

import logging
import time
try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - local environment only
    def load_dotenv(*args, **kwargs):
        return False

from fastapi import FastAPI

from .config import get_settings
from .routes import router
from .storage import EmailStore

load_dotenv()


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

    app = FastAPI(title="App Correos")
    app.state.settings = settings
    app.state.email_store = EmailStore(settings)

    @app.on_event("startup")
    async def startup_event() -> None:
        app.state.email_store.bootstrap()
        if app.state.email_store.ready:
            return
        time.sleep(1)

    app.include_router(router)
    return app


app = create_app()
