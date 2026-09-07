"""Tests for email listing views."""

from asyncio import run

from correos_app.routes import emails_view, list_emails, send_email
from conftest import FakeEmail, make_request


def test_api_list_emails_returns_json(store_factory):
    store_factory([
        FakeEmail(1, "ana@correo.com", "Hola", "Mensaje de prueba", "2026-08-17T10:00:00"),
    ])
    request = make_request("/api/emails")

    response = run(list_emails(request))

    assert response["status"] == "ok"
    assert len(response["emails"]) == 1
    assert response["emails"][0]["destinatario"] == "ana@correo.com"


def test_emails_view_renders_list(store_factory):
    store_factory([
        FakeEmail(1, "ana@correo.com", "Hola", "Mensaje de prueba", "2026-08-17T10:00:00"),
    ])
    request = make_request("/emails")

    response = run(emails_view(request))

    assert response.status_code == 200
    assert response.template.name == "emails.html"
    assert response.context["emails"][0].destinatario == "ana@correo.com"


def test_send_email_persists_and_returns_201(store_factory):
    store = store_factory()
    request = make_request("/send-email", method="POST", headers={"content-type": "application/json"})

    async def fake_json():
        return {
            "destinatario": "maria@correo.com",
            "asunto": "Prueba",
            "mensaje": "Contenido de prueba",
        }

    request.json = fake_json

    response = run(send_email(request))

    assert response.status_code == 201
    assert response.body is not None
    assert store.list_emails()[0].destinatario == "maria@correo.com"
