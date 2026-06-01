"""FastAPI application for email service."""

from fastapi import FastAPI, Form, Request
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
)
from fastapi.templating import Jinja2Templates

app = FastAPI(title="App Correos")
templates = Jinja2Templates(directory="templates")


FAKE_USERS = {"admin@correos.com": "secret123"}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.post("/login", response_class=HTMLResponse)
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


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")


@app.post("/send-email")
async def send_email(
    destinatario: str = Form(...),
    asunto: str = Form(...),
    mensaje: str = Form(...),
):
    # Aquí iría la lógica real de envío; por ahora devuelve confirmación
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "mensaje": f"Correo enviado a {destinatario} con asunto '{asunto}'",
        },
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
