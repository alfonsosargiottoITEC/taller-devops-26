# Taller DevOps — App Correos

Aplicación de ejemplo para el taller DevOps 2026. Sirve un formulario de envío de correos usando FastAPI + Jinja2.

## Requisitos

- Python 3.10+

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Levantar la app

```bash
source .venv/bin/activate   # si no está activo
uvicorn app:app --reload
```

La app queda disponible en [http://localhost:8000](http://localhost:8000).

## Endpoints

| Método | Ruta           | Descripción                                 |
|--------|----------------|---------------------------------------------|
| GET    | `/`            | Formulario de redacción de correo           |
| GET    | `/login`       | Pantalla de login                           |
| GET    | `/dashboard`   | Dashboard                                   |
| POST   | `/send-email`  | Envía un correo (form: destinatario, asunto, mensaje) |
| GET    | `/health`      | Health check                                |
| GET    | `/docs`        | Documentación interactiva (Swagger UI)      |

## Estructura

```
app.py              # Aplicación FastAPI
requirements.txt    # Dependencias
templates/
  index.html        # Formulario de correo
  login.html        # Pantalla de login
  dashboard.html    # Dashboard
Dockerfile          # Imagen Docker
docker-compose.yml  # Composición de servicios
```

