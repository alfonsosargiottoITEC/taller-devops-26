# Taller DevOps — App Correos

Aplicación de ejemplo para el taller DevOps 2026. Sirve un formulario de envío de correos con FastAPI + Jinja2 y persiste los envíos en PostgreSQL cuando se levanta con Docker.

## Quick path

1. Copiá el archivo de entorno:

   ```bash
   cp .env.example .env
   ```

2. Revisá los valores de conexión a la base:

   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`
   - `POSTGRES_DB`
   - `DB_HOST=db`
   - `DB_PORT=5432`
   - `DATABASE_URL` vacío o armado por vos si querés sobrescribir los valores anteriores

3. Levantá los servicios:

   ```bash
   docker compose up --build
   ```

4. Abrí la app en:

   - http://localhost:8000
   - http://localhost:8000/login
   - http://localhost:8000/docs

## Requisitos locales

Si querés correr la app fuera de Docker:

- Python 3.10+
- Dependencias instaladas con `pip install -r requirements.txt`
- Una instancia de PostgreSQL accesible desde la variable `DATABASE_URL`

## Variables de entorno

El proyecto toma sus valores desde `.env`.

| Variable | Qué hace |
|---|---|
| `APP_ENV` | Entorno de ejecución (`development`, `production`, etc.). |
| `SECRET_KEY` | Clave de aplicación. |
| `LOG_LEVEL` | Nivel de logs de la app. |
| `PORT` | Puerto publicado por Docker. |
| `POSTGRES_USER` | Usuario de la base. |
| `POSTGRES_PASSWORD` | Contraseña de la base. |
| `POSTGRES_DB` | Nombre de la base. |
| `DB_HOST` | Host de PostgreSQL dentro de la red Docker. |
| `DB_PORT` | Puerto de PostgreSQL dentro de la red Docker. |
| `DATABASE_URL` | Cadena de conexión completa. Si está vacía, la app la arma con los valores anteriores. |
| `SQLITE_PATH` | Ruta de respaldo local si no hay driver/DB disponible. |
| `DATABASE_CONNECT_TIMEOUT` | Timeout de conexión a la base, en segundos. |
| `SMTP_SERVER` | Servidor SMTP de ejemplo. |
| `SMTP_PORT` | Puerto SMTP. |
| `SMTP_USER` | Usuario SMTP. |
| `SMTP_PASSWORD` | Password SMTP. |

## Docker

Levantá todo en primer plano:

```bash
docker compose up --build
```

Levantá todo en detached:

```bash
docker compose up --build -d
```

Logs útiles:

```bash
docker compose logs -f app
docker compose logs -f db
docker compose logs -f app db
```

Tests desde la terminal del host, pero ejecutados dentro del contenedor:

```bash
docker compose run --rm app pytest
```

Si ya levantaste los servicios, también podés usar:

```bash
docker compose exec app pytest
```

Si cambiaste credenciales de Postgres y el volumen quedó con estado viejo, reinicializalo una vez:

```bash
docker compose down -v
docker compose up --build
```

### Conexión a la base

La app usa `DATABASE_URL` si está definida. Si la dejás vacía, arma la conexión con:

> Importante: `5433` es solo el puerto publicado en tu máquina. Dentro de Docker, la app debe conectar a `db:5432`.

```text
postgresql://<POSTGRES_USER>:<POSTGRES_PASSWORD>@<DB_HOST>:<DB_PORT>/<POSTGRES_DB>
```

Ejemplo típico dentro de Docker:

```text
postgresql://postgres:postgres@db:5432/correos_db
```

### Entrar a la base manualmente

```bash
docker compose exec db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

Una vez adentro, podés ver los correos guardados con:

```sql
\dt
SELECT * FROM sent_emails ORDER BY id DESC;
```

## Dónde se guardan los correos

Los correos enviados no se guardan como archivos HTML. Se persisten en PostgreSQL, en la tabla `sent_emails`.

Visualmente queda así:

```text
PostgreSQL (contenedor db)
└── tabla sent_emails
    ├── id
    ├── destinatario
    ├── asunto
    ├── mensaje
    └── created_at

Logs de la app
└── /var/log/app-correos/app.log
```

En Docker, la persistencia de datos vive en el volumen `db-data`.

## Verificación útil

- `GET /health` para revisar el estado de la app.
- `POST /send-email` para guardar un correo de prueba.
- `docker compose logs -f app` para seguir los logs.
- `docker compose logs -f db` para ver el arranque de PostgreSQL.
- `docker compose down -v` para resetear el volumen cuando cambian credenciales.

## Comandos útiles

```bash
docker compose logs -f app
docker compose logs -f db
docker compose exec db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
docker compose down
docker compose down -v
```

- `logs -f`: ver logs en vivo.
- `exec db psql`: entrar a la base.
- `down`: parar los servicios.
- `down -v`: parar y borrar volúmenes.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Formulario de redacción de correo |
| GET | `/login` | Pantalla de login |
| GET | `/dashboard` | Dashboard |
| POST | `/login` | Validación de credenciales |
| POST | `/send-email` | Guarda un correo en la base |
| GET | `/health` | Health check |
| GET | `/docs` | Documentación interactiva (Swagger UI) |

## Estructura

```text
app.py              # Entrada mínima de la app
correos_app/
  main.py           # Arma la aplicación FastAPI
  routes.py         # Rutas HTTP
  storage.py        # Persistencia de correos
  config.py         # Variables de entorno
  schemas.py        # Modelos de datos
requirements.txt    # Dependencias de Python
docker-compose.yml  # Servicios app + PostgreSQL
Dockerfile          # Imagen de la app
.env.example        # Variables para crear el .env
templates/
  index.html        # Formulario de correo
  login.html        # Pantalla de login
  dashboard.html    # Dashboard
```

## Recomendación

- Para explicar Docker y Compose, dejá esta regla clara: `5433` es el puerto visible desde el host, pero la app siempre habla con `db:5432` dentro de la red.
- Si cambian usuario, password o nombre de la base, hacé `docker compose down -v` antes de volver a levantar.
- Para clases o demos, `docker compose up --build -d` + `docker compose logs -f app` suele ser el flujo más cómodo.
