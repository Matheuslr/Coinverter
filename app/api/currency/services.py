"""
isort:skip_file
"""
from abc import ABC, abstractmethod
from typing import Dict, List

from bson.objectid import ObjectId

from app.api.currency.model import (
    CurrenciesPriceOutputSchema,
    CurrencySchema,
    CurrencyUpdateInputSchema,
)
from app.api.currency.repository.currency_api import CurrencyExternalAPIRepository
from app.api.currency.repository.database import CurrencyRepository
from app.api.helpers.exception import (
    CurrencyAlreadyExistException,
    CurrencyDoesNotExistException,
    NoCurrencyFoundException,
)
from app.db.mongodb import AsyncIOMotorClient
from app.settings import Settings


class CurrencyServiceAbstract(ABC):
    @abstractmethod
    def get_currencies(self):
        raise NotImplementedError

    @abstractmethod
    def create_currency(self, new_currency_schema: CurrencySchema):
        raise NotImplementedError

    @abstractmethod
    def get_currencies_price(self, CurrenciesPriceInputSchema) -> List[Dict]:
        raise NotImplementedError

    @abstractmethod
    def update_currency(
        self, _id: str, update_currency_schema: CurrencyUpdateInputSchema
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_currency(self, _id: ObjectId) -> None:
        raise NotImplementedError


class CurrencyService(CurrencyServiceAbstract):
    def __init__(self, conn: AsyncIOMotorClient, settings: Settings):
        self.currency_repository = CurrencyRepository(settings, conn)
        self.currency_external_api_repository = CurrencyExternalAPIRepository(settings)

    async def get_currencies(self) -> List[CurrencySchema]:
        return await self.currency_repository.get_currencies()

    async def create_currency(
        self, new_currency_schema: CurrencySchema
    ) -> CurrencySchema:  # noqa
        await self.__check_if_iso_4217_exists(new_currency_schema.iso_4217)

        currency: CurrencySchema = (
            await self.currency_repository.get_currency_by_iso_4217(
                new_currency_schema.iso_4217
            )
        )

        is_currency_already_created = currency is not None

        if is_currency_already_created:
            raise CurrencyAlreadyExistException

        return await self.currency_repository.create_currency(
            new_currency_schema
        )  # no qa

    async def get_currencies_price(
        self, CurrenciesPriceInputSchema
    ) -> List[CurrenciesPriceOutputSchema]:
        await self.__check_if_iso_4217_exists(CurrenciesPriceInputSchema.base_currency)

        currencies: List[
            CurrencySchema
        ] = await self.currency_repository.get_currencies()

        if len(currencies) == 0:
            raise NoCurrencyFoundException

        currencies_iso4217 = [item.iso_4217 for item in currencies]
        currencies_price = (
            await self.currency_external_api_repository.get_currencies_price(
                currencies_iso4217,
                CurrenciesPriceInputSchema.amount,
                CurrenciesPriceInputSchema.base_currency,
            )
        )
        response_list = []

        for currency in currencies:
            response_list.append(
                CurrenciesPriceOutputSchema(
                    name=currency.name,
                    iso_4217=currency.iso_4217,
                    amount=currencies_price[currency.iso_4217],
                )
            )

        return response_list

    async def update_currency(
        self, _id: str, update_currency_schema: CurrencyUpdateInputSchema
    ) -> None:
        update_dict: dict = await self.currency_repository.get_currency_by__id(
            ObjectId(_id)
        )

        if not update_dict:
            raise CurrencyDoesNotExistException
        del update_dict["_id"]
        if update_currency_schema.iso_4217:
            await self.__check_if_iso_4217_exists(update_currency_schema.iso_4217)

            currency = await self.currency_repository.get_currency_by_iso_4217(
                update_currency_schema.iso_4217
            )
            if currency:
                raise CurrencyAlreadyExistException

            update_dict["iso_4217"] = update_currency_schema.iso_4217

        if update_currency_schema.name:
            update_dict["name"] = update_currency_schema.name

        await self.currency_repository.update_currency(_id, update_dict)

    async def delete_currency(self, _id: ObjectId) -> None:
        currency = await self.currency_repository.get_currency_by__id(ObjectId(_id))

        if not currency:
            raise CurrencyDoesNotExistException

        await self.currency_repository.delete_currency(ObjectId(_id))

    async def __check_if_iso_4217_exists(self, iso_4217):
        is_currency_exists = (
            await self.currency_external_api_repository.check_if_currency_exist(
                iso_4217
            )
        )
        if not is_currency_exists:
            raise CurrencyDoesNotExistException
