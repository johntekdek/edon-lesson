"""FastAPI application factory — the one backend deployable (AD-1)."""

from fastapi import FastAPI

from edon.api.routers.health import router as health_router
from edon.config.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="e-DON Lesson Studio")  # i18n-ok — OpenAPI metadata, not user copy
    app.include_router(health_router, prefix="/api/v1")
    return app
