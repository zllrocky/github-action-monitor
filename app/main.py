from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers.health import health_router
from app.core.config import get_settings, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app():
    settings = get_settings()
    setup_logging(settings.LOG_LEVEL)
    app = FastAPI(lifespan=lifespan)
    app.include_router(health_router)
    return app
