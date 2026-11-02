from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin import setup_admin
from app.api import health, items, predict
from app.core.config import get_settings
from app.core.errors import register_error_handlers
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="Hackathon API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(items.router)
    app.include_router(predict.router)
    setup_admin(app)
    return app


app = create_app()
