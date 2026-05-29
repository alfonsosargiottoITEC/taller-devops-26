"""Tests for the /login endpoint."""
import pytest
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_login_exitoso():
    """Login con credenciales válidas devuelve 200 y redirect al dashboard."""
    response = client.post(
        "/login",
        data={"email": "admin@correos.com", "password": "secret123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["redirect"] == "/dashboard"


def test_login_fallido_password_incorrecta():
    """Login con password incorrecta devuelve 401."""
    response = client.post(
        "/login",
        data={"email": "admin@correos.com", "password": "wrongpass"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["status"] == "error"
    assert "inválidas" in body["detail"]


def test_login_fallido_usuario_inexistente():
    """Login con email que no existe devuelve 401."""
    response = client.post(
        "/login",
        data={"email": "noexiste@correos.com", "password": "cualquier"},
    )
    assert response.status_code == 401
    assert response.json()["status"] == "error"
