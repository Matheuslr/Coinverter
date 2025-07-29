from unittest.mock import MagicMock, patch

import httpx
import pytest
from deepdiff import DeepDiff
from fastapi.testclient import TestClient
from mongomock import MongoClient, ObjectId
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from app.settings import settings


@pytest.mark.asyncio
async def test_get_all_currencies_view(client: TestClient, mongo_db: MongoClient):
    response = client.get("/api/currency/")

    result = response.json()
    result_ids = set([item["_id"] for item in result])

    database_currencies_cursor = mongo_db[settings.mongo_test_database_name][
        settings.currency_collection_name
    ].find()
    database_ids = set([item["_id"].__str__() for item in database_currencies_cursor])
    assert result_ids == database_ids
    assert response.status_code == HTTP_200_OK


def test_shoud_create_a_currency(client: TestClient, currency_payload: dict):
    response = client.post("/api/currency/", json=currency_payload)
    result = response.json()
    del result["_id"]

    assert result == currency_payload
    assert response.status_code == HTTP_201_CREATED


@pytest.mark.parametrize(
    "wrong_iso",
    ["BR", "BRLL", "123", ""],
)
def test_shoud_not_create_a_currency_with_wrong_iso_4217(
    client: TestClient, currency_payload: dict, wrong_iso
):
    wrong_currency_payload = currency_payload.copy()
    wrong_currency_payload["iso_4217"] = wrong_iso
    response = client.post("/api/currency/", json=wrong_currency_payload)

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


def test_shoud_not_create_a_currency_with_inexistent_iso_4217(
    client: TestClient,
    currency_payload: dict,
):
    with patch(
        "app.api.currency.repository.currency_api.CurrencyExternalAPIRepository.check_if_currency_exist"
    ) as mocky:
        mocky.return_value = False
        wrong_currency_payload = currency_payload.copy()
        wrong_currency_payload["iso_4217"] = "XMR"
        response = client.post("/api/currency/", json=wrong_currency_payload)
        assert response.status_code == HTTP_404_NOT_FOUND


def test_shoud_not_create_an_already_created_currency(
    client: TestClient, currency_payload: dict
):
    with patch(
        "app.api.currency.repository.currency_api.CurrencyExternalAPIRepository.check_if_currency_exist"
    ) as mocky:
        mocky.return_value = True
        wrong_currency_payload = currency_payload.copy()
        wrong_currency_payload["iso_4217"] = "BRL"
        response = client.post("/api/currency/", json=wrong_currency_payload)

    assert response.status_code == HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_shoud_not_create_currency_when_external_service_is_down(
    client: TestClient, currency_payload: dict
):
    with patch(
        "app.api.currency.repository.currency_api.httpx.AsyncClient.get"
    ) as mocky:
        mocky.side_effect = httpx.RequestError("error")
        response = client.post("/api/currency/", json=currency_payload)

    assert response.status_code == HTTP_503_SERVICE_UNAVAILABLE


@patch(
    "app.api.currency.repository.currency_api.CurrencyExternalAPIRepository.check_if_currency_exist"
)
def test_shoud_get_currencies_price(
    mock_check_if_currency_exist: MagicMock,
    client: TestClient,
    mongo_db: MongoClient,
    currencies_payload: dict,
    exchangerate_api_response: dict,
    currencies_price_payload: dict,
):

    expected_payload = [
        {"name": "real", "iso_4217": "BRL", "amount": 1.0},
        {"name": "dolar", "iso_4217": "USD", "amount": 0.2},
    ]
    mock_check_if_currency_exist.return_value = True
    mongo_db[settings.mongo_test_database_name][
        settings.currency_collection_name
    ].insert_many(currencies_payload)
    with patch(
        "app.api.currency.repository.currency_api.CurrencyExternalAPIRepository.get_currencies_price"
    ) as mocky:
        mocky.return_value = exchangerate_api_response["rates"]
        response = client.post(
            "/api/currency/currencies-price", json=currencies_price_payload
        )
        result = response.json()
        assert DeepDiff(expected_payload, result)
        assert response.status_code == HTTP_200_OK


@pytest.mark.parametrize(
    "wrong_iso",
    ["BR", "BRLL", "123", ""],
)
def test_shoud_not_get_currencies_price_with_wrong_iso_4217(
    client: TestClient, currencies_price_payload: dict, wrong_iso
):
    wrong_currency_payload = currencies_price_payload.copy()
    wrong_currency_payload["base_currency"] = wrong_iso
    response = client.post(
        "/api/currency/currencies-price", json=wrong_currency_payload
    )

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


def test_shoud_not_get_currencies_price_with_empty_database(
    client: TestClient,
    currencies_price_payload: dict,
):
    with patch(
        "app.api.currency.repository.database.CurrencyRepository.get_currencies"
    ) as mocky:
        mocky.return_value = []
        wrong_currency_payload = currencies_price_payload.copy()
        wrong_currency_payload["iso_4217"] = "BRL"
        response = client.post(
            "/api/currency/currencies-price", json=wrong_currency_payload
        )
        assert response.status_code == HTTP_404_NOT_FOUND


def test_shoud_not_get_currencies_price_with_inexistent_iso_4217(
    client: TestClient,
    currencies_price_payload: dict,
):
    with patch(
        "app.api.currency.repository.currency_api.CurrencyExternalAPIRepository.check_if_currency_exist"
    ) as mocky:
        mocky.return_value = False
        wrong_currency_payload = currencies_price_payload.copy()
        wrong_currency_payload["iso_4217"] = "XMR"
        response = client.post(
            "/api/currency/currencies-price", json=wrong_currency_payload
        )
        assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_shoud_not_get_currencies_price_when_external_service_is_down(
    client: TestClient, currencies_price_payload: dict
):
    with patch(
        "app.api.currency.repository.currency_api.httpx.AsyncClient.get"
    ) as mocky:
        mocky.side_effect = httpx.RequestError("error")
        response = client.post(
            "/api/currency/currencies-price", json=currencies_price_payload
        )

    assert response.status_code == HTTP_503_SERVICE_UNAVAILABLE


@patch(
    "app.api.currency.repository.currency_api.CurrencyExternalAPIRepository.check_if_currency_exist"
)
def test_should_update_currency(
    mock_check_if_currency_exists: MagicMock,
    client: TestClient,
    mongo_db: MongoClient,
    currency_payload: dict,
):
    mock_check_if_currency_exists.return_value = True

    mongo_db[settings.mongo_test_database_name][
        settings.currency_collection_name
    ].insert_one(currency_payload)

    currency_id = currency_payload["_id"].__str__()

    update_dict = dict(iso_4217="USD", name="Dolar")

    response = client.patch(f"/api/currency/{currency_id}", json=update_dict)

    assert response.status_code == HTTP_204_NO_CONTENT

    new_currency = mongo_db[settings.mongo_test_database_name][
        settings.currency_collection_name
    ].find_one({"_id": ObjectId(currency_id)})

    assert new_currency["name"] == update_dict["name"]
    assert new_currency["iso_4217"] == update_dict["iso_4217"]


@patch(
    "app.api.currency.repository.currency_api.CurrencyExternalAPIRepository.check_if_currency_exist"
)
def test_should_partial_update_currency_with_missing_name(
    mock_check_if_currency_exists: MagicMock,
    client: TestClient,
    mongo_db: MongoClient,
    currency_payload: dict,
):
    mock_check_if_currency_exists.return_value = True

    mongo_db[settings.mongo_test_database_name][
        settings.currency_collection_name
    ].insert_one(currency_payload)

    currency_id = currency_payload["_id"].__str__()

    update_dict = dict(
        iso_4217="USD",
    )

    response = client.patch(f"/api/currency/{currency_id}", json=update_dict)

    assert response.status_code == HTTP_204_NO_CONTENT

    new_currency = mongo_db[settings.mongo_test_database_name][
        settings.currency_collection_name
    ].find_one({"_id": ObjectId(currency_id)})

    assert new_currency["name"] == currency_payload["name"]
    assert new_currency["iso_4217"] == update_dict["iso_4217"]


@patch(
    "app.api.currency.repository.currency_api.CurrencyExternalAPIRepository.check_if_currency_exist"
)
def test_should_partial_update_currency_with_missing_iso_4217(
    mock_check_if_currency_exists: MagicMock,
    client: TestClient,
    mongo_db: MongoClient,
    currency_payload: dict,
):
    mock_check_if_currency_exists.return_value = True

    mongo_db[settings.mongo_test_database_name][
        settings.currency_collection_name
    ].insert_one(currency_payload)

    currency_id = currency_payload["_id"].__str__()

    update_dict = dict(
        name="Dolar",
    )

    response = client.patch(f"/api/currency/{currency_id}", json=update_dict)

    assert response.status_code == HTTP_204_NO_CONTENT

    new_currency = mongo_db[settings.mongo_test_database_name][
        settings.currency_collection_name
    ].find_one({"_id": ObjectId(currency_id)})

    assert new_currency["name"] == update_dict["name"]
    assert new_currency["iso_4217"] == currency_payload["iso_4217"]


@pytest.mark.asyncio
async def test_shoud_not_get_update_when_external_service_is_down(
    client: TestClient, mongo_db: MongoClient, currency_payload: dict
):
    mongo_db[settings.mongo_test_database_name][
        settings.currency_collection_name
    ].insert_one(currency_payload)
    with patch(
        "app.api.currency.repository.currency_api.httpx.AsyncClient.get"
    ) as mocky:
        mocky.side_effect = httpx.RequestError("error")

        currency_id = currency_payload["_id"].__str__()

        update_dict = dict(iso_4217="USD", name="Dolar")
        mocky.side_effect = httpx.RequestError("error")
        response = client.patch(f"/api/currency/{currency_id}", json=update_dict)

    assert response.status_code == HTTP_503_SERVICE_UNAVAILABLE


@pytest.mark.parametrize(
    "wrong_iso",
    ["BR", "BRLL", "123", ""],
)
def test_shoud_not_update_currency_with_wrong_iso_4217(
    client: TestClient, mongo_db: MongoClient, currency_payload: dict, wrong_iso: str
):
    mongo_db[settings.mongo_test_database_name][
        settings.currency_collection_name
    ].insert_one(currency_payload)

    with patch(
        "app.api.currency.repository.currency_api.httpx.AsyncClient.get"
    ) as mocky:
        mocky.side_effect = httpx.RequestError("error")

        currency_id = currency_payload["_id"].__str__()

        update_dict = dict(iso_4217=wrong_iso, name="Dolar")
        response = client.patch(f"/api/currency/{currency_id}", json=update_dict)

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


def test_shoud_not_update_with_empty_database(
    client: TestClient,
    mongo_db: MongoClient,
    currency_payload: dict,
):
    mongo_db[settings.mongo_test_database_name][
        settings.currency_collection_name
    ].insert_one(currency_payload)

    with patch(
        "app.api.currency.repository.database.CurrencyRepository.get_currency_by__id"
    ) as mocky:
        mocky.return_value = []
        currency_id = currency_payload["_id"].__str__()
        update_dict = dict(iso_4217="USD", name="Dolar")
        response = client.patch(f"/api/currency/{currency_id}", json=update_dict)
        assert response.status_code == HTTP_404_NOT_FOUND


def test_shoud_not_update_currency_with_inexistent_iso_4217(
    client: TestClient,
    mongo_db: MongoClient,
    currency_payload: dict,
):
    mongo_db[settings.mongo_test_database_name][
        settings.currency_collection_name
    ].insert_one(currency_payload)

    with patch(
        "app.api.currency.repository.currency_api.CurrencyExternalAPIRepository.check_if_currency_exist"
    ) as mocky:
        mocky.return_value = False
        currency_id = currency_payload["_id"].__str__()
        update_dict = dict(iso_4217="XNR", name="Real")
        response = client.patch(f"/api/currency/{currency_id}", json=update_dict)
        assert response.status_code == HTTP_404_NOT_FOUND


def test_shoud_not_update_a_currency_if_iso_4217_already_exists(
    client: TestClient, currency_payload: dict, mongo_db: MongoClient
):
    mongo_db[settings.mongo_test_database_name][
        settings.currency_collection_name
    ].insert_one(currency_payload)
    with patch(
        "app.api.currency.repository.currency_api.CurrencyExternalAPIRepository.check_if_currency_exist"
    ) as mocky:
        mocky.return_value = currency_payload
        currency_id = currency_payload["_id"].__str__()
        update_dict = dict(iso_4217="BRL", name="Real")
        response = client.patch(f"/api/currency/{currency_id}", json=update_dict)
    assert response.status_code == HTTP_409_CONFLICT


def test_should_delete_a_currency(
    client: TestClient, mongo_db: MongoClient, currency_payload: dict
):
    mongo_db[settings.mongo_test_database_name][
        settings.currency_collection_name
    ].insert_one(currency_payload)

    currency_id = currency_payload["_id"].__str__()

    response = client.delete(f"/api/currency/{currency_id}")

    assert response.status_code == HTTP_204_NO_CONTENT

    new_currency = mongo_db[settings.mongo_test_database_name][
        settings.currency_collection_name
    ].find_one({"_id": ObjectId(currency_id)})

    assert new_currency is None


def test_should_not_delete_a_inexistent_currency(
    client: TestClient, mongo_db: MongoClient, currency_payload: dict
):
    mongo_db[settings.mongo_test_database_name][
        settings.currency_collection_name
    ].insert_one(currency_payload)

    currency_id = currency_payload["_id"].__str__()
    with patch(
        "app.api.currency.repository.database.CurrencyRepository.get_currency_by__id"
    ) as mocky:
        mocky.return_value = []
        response = client.delete(f"/api/currency/{currency_id}")

        assert response.status_code == HTTP_404_NOT_FOUND

        new_currency = mongo_db[settings.mongo_test_database_name][
            settings.currency_collection_name
        ].find_one({"_id": ObjectId(currency_id)})

        assert new_currency is not None
