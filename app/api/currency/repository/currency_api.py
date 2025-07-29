from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, List

import httpx

from app.api.helpers.exception import ExternalAPIUnreachableException
from app.settings import Settings, settings


class CurrencyExternalAPIRepositoryAbstract(ABC):
    @abstractmethod
    def check_if_currency_exist(self, iso_4217: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_currencies_price(
        self, base_currency: str, currencies_list: List[str], amount: Decimal
    ) -> List[Dict]:
        raise NotImplementedError

    @abstractmethod
    def _url_builder(
        self,
        currencies_list: List[str],
        amount: Decimal = None,
        base_currency: str = None,
    ) -> str:
        raise NotImplementedError


class CurrencyExternalAPIRepository(CurrencyExternalAPIRepositoryAbstract):
    def __init__(self, settings: Settings):
        self._settings = settings

    async def check_if_currency_exist(self, iso_4217: str):
        url_query = f"{settings.currency_api_url}/currencies"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url_query)
                if iso_4217.upper() in response.json().keys():
                    return True
                return False
            except httpx.RequestError:
                raise ExternalAPIUnreachableException

    async def get_currencies_price(
        self,
        currencies_list: List[str],
        amount: Decimal = None,
        base_currency: str = None,
    ) -> List[Dict]:
        url_query = self._url_builder(currencies_list, amount, base_currency)
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url_query)
                rates = response.json()["rates"]

                return rates
            except httpx.RequestError:
                raise ExternalAPIUnreachableException

    def _url_builder(
        self,
        currencies_list: List[str],
        amount: Decimal = None,
        base_currency: str = None,
    ) -> str:
        str_currencies = ",".join(currencies_list)
        url_query = (
            f"{settings.currency_api_url}/latest?currencies={str_currencies}&places=2"
        )
        if amount:
            str_amount = str(Decimal(amount).quantize(Decimal("1.00")))
            url_query += f"&amount={str_amount}"
        if base_currency:
            url_query += f"&base={base_currency}"
        return url_query
