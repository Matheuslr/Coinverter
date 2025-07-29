from typing import Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import httpx
import pytest

from app.api.currency.repository.currency_api import CurrencyExternalAPIRepository
from app.api.helpers.exception import ExternalAPIUnreachableException
from app.settings import settings


@pytest.mark.asyncio
async def test_should_get_currency_by_iso_4217(currencies_payload: Dict):
    mock_currency_repository = AsyncMock()
    mock_currency_repository.get_currencies = AsyncMock(return_value=currencies_payload)

    repositories = await mock_currency_repository.get_currencies()

    assert repositories == currencies_payload
    assert mock_currency_repository.get_currencies.call_count == 1


def test_should_create_url_with_all_parameters():
    currency_external_api: CurrencyExternalAPIRepository = (
        CurrencyExternalAPIRepository(settings)
    )
    list_currencies = ["BRL", "USD", "EUR"]
    amount = 50.00
    base_currency = "BRL"

    url = currency_external_api._url_builder(list_currencies, amount, base_currency)

    assert (
        url
        == "https://api.fxratesapi.com/latest?currencies=BRL,USD,EUR&places=2&amount=50.00&base=BRL"
    )


def test_should_create_url_with_missing_amount_parameters():
    currency_external_api: CurrencyExternalAPIRepository = (
        CurrencyExternalAPIRepository(settings)
    )
    list_currencies = ["BRL", "USD", "EUR"]
    amount = None
    base_currency = "BRL"

    url = currency_external_api._url_builder(list_currencies, amount, base_currency)

    assert (
        url
        == "https://api.fxratesapi.com/latest?currencies=BRL,USD,EUR&places=2&base=BRL"
    )


def test_should_create_url_with_missing_list_currencies_parameters():
    currency_external_api: CurrencyExternalAPIRepository = (
        CurrencyExternalAPIRepository(settings)
    )
    list_currencies = ["BRL", "USD", "EUR"]
    amount = 50.00
    base_currency = None

    url = currency_external_api._url_builder(list_currencies, amount, base_currency)

    assert (
        url
        == "https://api.fxratesapi.com/latest?currencies=BRL,USD,EUR&places=2&amount=50.00"
    )


@pytest.mark.asyncio
@patch("app.api.currency.repository.currency_api.httpx.AsyncClient.get")
async def test_should_create_url_with_missing_amount_and_list_currencies_parameters(
    mock_httpx: MagicMock,
):
    currency_external_api: CurrencyExternalAPIRepository = (
        CurrencyExternalAPIRepository(settings)
    )
    list_currencies = ["BRL", "USD", "EUR"]
    amount = None
    base_currency = None

    url = currency_external_api._url_builder(list_currencies, amount, base_currency)

    assert url == "https://api.fxratesapi.com/latest?currencies=BRL,USD,EUR&places=2"


@pytest.mark.asyncio
@patch("app.api.currency.repository.currency_api.httpx.AsyncClient.get")
async def test_shoud_get_currencies_rates(
    mock_httpx: MagicMock, exchangerate_api_response: dict
):
    mock_httpx.return_value = Mock()
    mock_httpx.return_value.json.return_value = exchangerate_api_response
    currency_external_api: CurrencyExternalAPIRepository = (
        CurrencyExternalAPIRepository(settings)
    )
    list_currencies = ["BRL", "USD"]
    result = await currency_external_api.get_currencies_price(list_currencies)
    assert set(result) == set(exchangerate_api_response["rates"])


@pytest.mark.asyncio
@patch("app.api.currency.repository.currency_api.httpx.AsyncClient.get")
async def test_shoud_raise_exception_when_external_api_is_off(mock_httpx: MagicMock):
    mock_httpx.side_effect = httpx.RequestError("error")
    currency_external_api: CurrencyExternalAPIRepository = (
        CurrencyExternalAPIRepository(settings)
    )
    list_currencies = ["BRL", "USD", "EUR"]
    with pytest.raises(ExternalAPIUnreachableException):
        await currency_external_api.get_currencies_price(list_currencies)


@pytest.mark.asyncio
@patch("app.api.currency.repository.currency_api.httpx.AsyncClient.get")
async def test_shoud_return_false_when_iso_4217_does_not_exists(
    mock_httpx: MagicMock, exchangerate_api_response: dict
):
    mock_httpx.return_value = Mock()
    mock_httpx.return_value.json.return_value = exchangerate_api_response
    currency_external_api: CurrencyExternalAPIRepository = (
        CurrencyExternalAPIRepository(settings)
    )
    result = await currency_external_api.check_if_currency_exist("BRX")
    assert result == False
