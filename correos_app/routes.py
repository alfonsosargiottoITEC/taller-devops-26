"""HTTP routes for the app."""

from __future__ import annotations

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .schemas import EmailPayload

router = APIRouter()
templates = Jinja2Templates(directory="templates")
FAKE_USERS = {"admin@correos.com": "secret123"}


async def _read_email_payload(request: Request) -> EmailPayload:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        raw_payload = await request.json()
    else:
        raw_payload = dict(await request.form())
    return EmailPayload(**raw_payload)


def _get_email_store(request: Request):
    return request.app.state.email_store


def _serialize_email(email):
    if hasattr(email, "model_dump"):
        return email.model_dump()
    if hasattr(email, "dict"):
        return email.dict()
    return dict(email)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse(request, "login.html")


@router.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    if FAKE_USERS.get(email) == password:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        request,
        "login.html",
        {"error": "Credenciales inválidas. Revisá tu email y contraseña."},
        status_code=401,
    )


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")


@router.get("/emails", response_class=HTMLResponse)
async def emails_view(request: Request):
    store = _get_email_store(request)
    try:
        store.ensure_ready()
        emails = store.list_emails()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Base de datos no disponible: {exc}",
        ) from exc

    return templates.TemplateResponse(
        request,
        "emails.html",
        {"emails": emails},
    )


@router.get("/api/emails")
async def list_emails(request: Request):
    store = _get_email_store(request)
    try:
        store.ensure_ready()
        emails = store.list_emails()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Base de datos no disponible: {exc}",
        ) from exc

    return {"status": "ok", "emails": [_serialize_email(email) for email in emails]}


@router.post("/send-email")
async def send_email(request: Request):
    payload = await _read_email_payload(request)
    store = request.app.state.email_store
    try:
        store.ensure_ready()
        persisted = store.save(payload)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Base de datos no disponible: {exc}",
        ) from exc

    return JSONResponse(
        status_code=201,
        content={
            "status": "ok",
            "mensaje": f"Correo enviado a {payload.destinatario} con asunto '{payload.asunto}'",
            "stored_id": persisted["id"],
            "stored_at": persisted["created_at"],
        },
    )


@router.get("/health")
async def health(request: Request):
    store = request.app.state.email_store
    return {"status": "ok", **store.health()}
