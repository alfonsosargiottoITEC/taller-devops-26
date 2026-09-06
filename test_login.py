"""Tests for the /login endpoint."""

from asyncio import run

from correos_app.routes import login_post
from conftest import make_request


def test_login_exitoso(store_factory):
    """Login con credenciales válidas redirige al dashboard (303)."""
    store_factory()
    request = make_request("/login", method="POST")

    response = run(
        login_post(
            request,
            email="admin@correos.com",
            password="secret123",
        )
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"


def test_login_fallido_password_incorrecta(store_factory):
    """Login con password incorrecta devuelve 401 con mensaje en HTML."""
    store_factory()
    request = make_request("/login", method="POST")

    response = run(
        login_post(
            request,
            email="admin@correos.com",
            password="wrongpass",
        )
    )

    assert response.status_code == 401
    assert "Credenciales inválidas" in response.body.decode()


def test_login_fallido_usuario_inexistente(store_factory):
    """Login con email que no existe devuelve 401 con mensaje en HTML."""
    store_factory()
    request = make_request("/login", method="POST")

    response = run(
        login_post(
            request,
            email="noexiste@correos.com",
            password="cualquier",
        )
    )

    assert response.status_code == 401
    assert "Credenciales inválidas" in response.body.decode()
