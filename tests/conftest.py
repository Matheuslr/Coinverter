import pymongo
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.application import get_app
from app.settings import settings


@pytest.fixture()
def async_mongo_db():
    class DataBase:
        client: AsyncIOMotorClient = None

    db = DataBase()

    db.client = AsyncIOMotorClient(
        settings.mongo_test_url(),
        maxPoolSize=settings.mongo_max_connections_count,
        minPoolSize=settings.mongo_min_connections_count,
    )
    yield db.client

    db.client.close()


@pytest.fixture()
def mongo_db():
    client = pymongo.MongoClient(settings.mongo_test_url())
    yield client
    client[settings.mongo_test_database_name][settings.currency_collection_name].drop()
    client.close()


@pytest.fixture()
def client(async_mongo_db):
    with (TestClient(get_app())) as client:
        yield client


@pytest.fixture()
def currency_payload():
    return {"name": "real", "iso_4217": "BRL"}


@pytest.fixture()
def currencies_payload():
    return [{"name": "real", "iso_4217": "BRL"}, {"name": "dolar", "iso_4217": "USD"}]


@pytest.fixture()
def currencies_price_payload():
    return {"base_currency": "BRL", "amount": "50.00"}


@pytest.fixture()
def exchangerate_api_response() -> dict:
    return {
        "motd": {
            "msg": "If you or your company use this project or like what we doing, please consider backing us so we can continue maintaining and evolving this project.",
            "url": "https://exchangerate.host/#/donate",
        },
        "success": True,
        "base": "BRL",
        "date": "2022-04-29",
        "rates": {
            "BRL": 1.00,
            "USD": 0.20,
        },
    }
