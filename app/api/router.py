from fastapi import APIRouter

from app.api import docs, healthcheck
from app.api.currency.router import currency_router

api_router = APIRouter()
api_router.include_router(docs.router)
api_router.include_router(healthcheck.router, tags=["Healthcheck"])
api_router.include_router(currency_router)
