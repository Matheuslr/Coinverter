from pathlib import Path

from ddtrace import config
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination

from app.api.helpers.handler import register_exception_handlers
from app.api.helpers.middlewares import CatchExceptionsMiddleware
from app.api.router import api_router
from app.db.mongodb_utils import close_mongo_connection, connect_to_mongo
from app.settings import settings

APP_ROOT = Path(__file__).parent


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """

    # Override service name
    config.fastapi["service_name"] = str(settings.service_name)

    app = FastAPI(
        title="app",
        description="Fastapi API for currency exchange",
        # version=metadata.version("app"),
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(CatchExceptionsMiddleware)

    app.add_event_handler("startup", connect_to_mongo)
    app.add_event_handler("shutdown", close_mongo_connection)

    app.include_router(router=api_router)
    app.mount(
        "/static",
        StaticFiles(directory=APP_ROOT / "static"),
        name="static",
    )
    add_pagination(app)

    register_exception_handlers(app)
    return app
