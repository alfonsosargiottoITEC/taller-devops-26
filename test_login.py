"""Tests for login and route protection."""

from asyncio import run

from correos_app.main import create_app
from correos_app.routes import dashboard, index, login_post, logout
from conftest import make_request


def test_login_exitoso(store_factory):
    """Login con credenciales válidas redirige al dashboard y marca la sesión."""
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
    assert request.scope["session"]["authenticated"] is True
    assert request.scope["session"]["user"] == "admin@correos.com"


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
    assert request.scope["session"] == {}


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
    assert request.scope["session"] == {}


def test_ruta_protegida_sin_sesion_redirige_al_login(store_factory):
    store_factory()
    request = make_request("/")

    response = run(index(request))

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_ruta_protegida_con_sesion_renderiza_normalmente(store_factory):
    store_factory()
    request = make_request("/dashboard", session={"authenticated": True})

    response = run(dashboard(request))

    assert response.status_code == 200
    assert response.template.name == "dashboard.html"


def test_logout_limpia_sesion_y_redirige_al_login(store_factory):
    store_factory()
    request = make_request("/logout", session={"authenticated": True, "user": "admin@correos.com"})

    response = run(logout(request))

    assert response.status_code == 303
    assert response.headers["location"] == "/login"
    assert request.scope["session"] == {}


def test_docs_se_desactivan_en_produccion(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")

    app = create_app()

    assert app.docs_url is None
    assert app.redoc_url is None
    assert app.openapi_url is None


def _session_middleware_kwargs(app):
    for middleware in app.user_middleware:
        if middleware.cls.__name__ == "SessionMiddleware":
            return middleware.kwargs
    raise AssertionError("SessionMiddleware no configurado")


def test_cookie_de_sesion_es_segura_por_default_en_produccion(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("SESSION_COOKIE_SECURE", raising=False)

    app = create_app()

    assert _session_middleware_kwargs(app)["https_only"] is True


def test_cookie_de_sesion_puede_permitir_http_para_taller(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")

    app = create_app()

    assert _session_middleware_kwargs(app)["https_only"] is False
