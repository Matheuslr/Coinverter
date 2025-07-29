from fastapi.routing import APIRouter

from app.api.currency.views import router

currency_router = APIRouter()
currency_router.include_router(router, prefix="/api/currency")
