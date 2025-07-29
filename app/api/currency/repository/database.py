from abc import ABC, abstractmethod
from typing import List

from bson.objectid import ObjectId

from app.api.currency.model import CurrencySchema
from app.db.mongodb import AsyncIOMotorClient
from app.settings import Settings


class CurrencyRepositoryAbstract(ABC):
    @abstractmethod
    def get_currency_by_iso_4217(self, iso_4217: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_currency_by__id(self, _id: ObjectId) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_currencies(self) -> List[CurrencySchema]:
        raise NotImplementedError

    @abstractmethod
    def create_currency(self, name: str, iso_4217: str) -> CurrencySchema:
        raise NotImplementedError

    @abstractmethod
    def update_currency(
        self, _id: ObjectId, name: str = None, iso_4217: str = None
    ) -> CurrencySchema:
        raise NotImplementedError

    @abstractmethod
    def delete_currency(self, _id: ObjectId) -> CurrencySchema:
        raise NotImplementedError


class CurrencyRepository(CurrencyRepositoryAbstract):
    def __init__(self, settings: Settings, conn: AsyncIOMotorClient):
        self.conn = conn
        self._settings = settings
        self._database_name = (
            settings.mongo_test_database_name
            if settings.test
            else settings.mongo_database_name
        )

    async def get_currency_by_iso_4217(self, iso_4217: str) -> dict:
        return await self.conn[self._database_name][
            self._settings.currency_collection_name
        ].find_one({"iso_4217": iso_4217})

    async def get_currency_by__id(self, _id: ObjectId) -> dict:

        return await self.conn[self._database_name][
            self._settings.currency_collection_name
        ].find_one({"_id": _id})

    async def get_currencies(self, query={}) -> List[CurrencySchema]:
        currencies: List[CurrencySchema] = []

        rows = self.conn[self._database_name][
            self._settings.currency_collection_name
        ].find(query)

        async for row in rows:  # pragma: no cover
            currencies.append(CurrencySchema(**row))  # pragma: no cover

        return currencies  # pragma: no cover

    async def create_currency(
        self, new_currency_schema: CurrencySchema
    ) -> CurrencySchema:
        currency_dict = dict(
            name=new_currency_schema.name, iso_4217=new_currency_schema.iso_4217
        )
        await self.conn[self._database_name][
            self._settings.currency_collection_name
        ].insert_one(currency_dict)

        return CurrencySchema(**currency_dict)

    async def update_currency(self, _id: str, update_dict) -> CurrencySchema:

        await self.conn[self._database_name][
            self._settings.currency_collection_name
        ].find_one_and_update({"_id": ObjectId(_id)}, {"$set": update_dict})

    async def delete_currency(self, _id: ObjectId) -> None:
        await self.conn[self._database_name][
            self._settings.currency_collection_name
        ].find_one_and_delete({"_id": ObjectId(_id)})
