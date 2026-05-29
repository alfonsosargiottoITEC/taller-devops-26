"""Tests for the /login endpoint."""
from fastapi.testclient import TestClient

from app import app

client = TestClient(app, follow_redirects=False)


def test_login_exitoso():
    """Login con credenciales válidas redirige al dashboard (303)."""
    response = client.post(
        "/login",
        data={"email": "admin@correos.com", "password": "secret123"},
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"


def test_login_fallido_password_incorrecta():
    """Login con password incorrecta devuelve 401 con mensaje en HTML."""
    response = client.post(
        "/login",
        data={"email": "admin@correos.com", "password": "wrongpass"},
    )
    assert response.status_code == 401
    assert "Credenciales inválidas" in response.text


def test_login_fallido_usuario_inexistente():
    """Login con email que no existe devuelve 401 con mensaje en HTML."""
    response = client.post(
        "/login",
        data={"email": "noexiste@correos.com", "password": "cualquier"},
    )
    assert response.status_code == 401
    assert "Credenciales inválidas" in response.text
