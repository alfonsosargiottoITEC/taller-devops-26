"""Entry point for the FastAPI app."""
"""EDITED FROM HOST"""
from correos_app.main import app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
