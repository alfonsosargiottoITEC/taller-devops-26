FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Las dependencias se instalan antes que el código para aprovechar la caché.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# El contenedor no necesita ejecutar la aplicación como root.
RUN groupadd --system app && useradd --system --gid app --no-create-home app

# Se copia el proyecto completo. .dockerignore decide qué queda afuera.
COPY --chown=app:app . .

USER app

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
