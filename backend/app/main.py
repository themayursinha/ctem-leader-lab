import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.v1.admin import router as admin_router
from app.config import settings

logger = logging.getLogger("ctem")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.admin_token:
        logger.warning("CTEM_ADMIN_TOKEN is unset; mutating APIs are running in unsafe local demo mode.")
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="CTEM Leader Lab API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.cors_origins if origin.strip()],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    app.include_router(admin_router)

    return app


app = create_app()
