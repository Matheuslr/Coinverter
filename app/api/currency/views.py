"""
isort:skip_file
"""
from typing import Dict, List

from fastapi import APIRouter, Depends
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_412_PRECONDITION_FAILED,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from app.api.currency.model import (
    CurrenciesPriceInputSchema,
    CurrenciesPriceOutputSchema,
    CurrencySchema,
    CurrencyUpdateInputSchema,
    MessageError,
)
from app.api.currency.services import CurrencyService
from app.api.helpers.exception import (
    CurrencyAlreadyExistException,
    CurrencyDoesNotExistException,
    DomainException,
    ExternalAPIUnreachableException,
    HTTPError,
    NoCurrencyFoundException,
)
from app.db.mongodb import AsyncIOMotorClient, get_database
from app.settings import settings

router = APIRouter()


@router.get("/", status_code=HTTP_200_OK, response_model=List[CurrencySchema])
async def index(conn: AsyncIOMotorClient = Depends(get_database)):
    """
    List all currencies.


    :return: list of currency
    """
    try:
        currency_service: CurrencyService = CurrencyService(conn, settings)
        return await currency_service.get_currencies()

    except Exception as e:  # pragma: no cover
        raise e  # pragma: no cover


@router.post(
    "/",
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_404_NOT_FOUND: {"model": MessageError},
        HTTP_409_CONFLICT: {"model": MessageError},
        HTTP_412_PRECONDITION_FAILED: {"model": MessageError},
        HTTP_503_SERVICE_UNAVAILABLE: {"model": MessageError},
    },
    response_model=CurrencySchema,
)
async def create(
    new_currency_schema: CurrencySchema,
    conn: AsyncIOMotorClient = Depends(get_database),
):
    """
    Create a currency.

    :param new_currency_schema: A currency schema

    :return: Currency
    """
    try:
        currency_service: CurrencyService = CurrencyService(conn, settings)
        return await currency_service.create_currency(new_currency_schema)

    except CurrencyAlreadyExistException as exception:
        raise HTTPError(
            status_code=HTTP_409_CONFLICT,
            error_message=str(exception),
            error_code=exception.error_code,
        )
    except CurrencyDoesNotExistException as exception:
        raise HTTPError(
            status_code=HTTP_404_NOT_FOUND,
            error_message=str(exception),
            error_code=exception.error_code,
        )
    except ExternalAPIUnreachableException as exception:
        raise HTTPError(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            error_message=str(exception),
            error_code=exception.error_code,
        )


@router.patch(
    "/{_id}",
    status_code=HTTP_204_NO_CONTENT,
    responses={
        HTTP_404_NOT_FOUND: {"model": MessageError},
        HTTP_409_CONFLICT: {"model": MessageError},
        HTTP_412_PRECONDITION_FAILED: {"model": MessageError},
        HTTP_503_SERVICE_UNAVAILABLE: {"model": MessageError},
    },
)
async def update(
    _id: str,
    update_currency_schema: CurrencyUpdateInputSchema,
    conn: AsyncIOMotorClient = Depends(get_database),
):
    """
    Update a currency.

    :param _id: A currency _id

    :param new_currency_schema: A currency schema

    :return: None
    """
    try:
        currency_service: CurrencyService = CurrencyService(conn, settings)
        await currency_service.update_currency(_id, update_currency_schema)

    except CurrencyAlreadyExistException as exception:
        raise HTTPError(
            status_code=HTTP_409_CONFLICT,
            error_message=str(exception),
            error_code=exception.error_code,
        )
    except (CurrencyDoesNotExistException, CurrencyDoesNotExistException) as exception:
        raise HTTPError(
            status_code=HTTP_404_NOT_FOUND,
            error_message=str(exception),
            error_code=exception.error_code,
        )
    except ExternalAPIUnreachableException as exception:
        raise HTTPError(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            error_message=str(exception),
            error_code=exception.error_code,
        )


@router.delete(
    "/{_id}",
    status_code=HTTP_204_NO_CONTENT,
    responses={
        HTTP_404_NOT_FOUND: {"model": MessageError},
    },
)
async def delete(
    _id: str,
    conn: AsyncIOMotorClient = Depends(get_database),
):
    """
    Delete a currency.

    :param _id: A currency _id

    :return: None
    """
    try:
        currency_service: CurrencyService = CurrencyService(conn, settings)
        await currency_service.delete_currency(_id)

    except (CurrencyDoesNotExistException, CurrencyDoesNotExistException) as exception:
        raise HTTPError(
            status_code=HTTP_404_NOT_FOUND,
            error_message=str(exception),
            error_code=exception.error_code,
        )


@router.post(
    "/currencies-price",
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": MessageError},
        HTTP_412_PRECONDITION_FAILED: {"model": MessageError},
        HTTP_503_SERVICE_UNAVAILABLE: {"model": MessageError},
    },
    response_model=List[CurrenciesPriceOutputSchema],
)
async def currencies_price(
    currencies_price: CurrenciesPriceInputSchema,
    conn: AsyncIOMotorClient = Depends(get_database),
):
    """
    List all saved currencies and price then based on base_iso_4217

    :param base_currency: Changing base currency. \
        Enter the three-letter currency code of your \
            preferred base currency.example:base=USD

    :param amount: [optional] The amount to be converted.

    :return: list of currency
    """
    try:
        currency_service: CurrencyService = CurrencyService(conn, settings)
        return await currency_service.get_currencies_price(currencies_price)

    except (NoCurrencyFoundException, CurrencyDoesNotExistException) as exception:

        raise HTTPError(
            status_code=HTTP_404_NOT_FOUND,
            error_message=str(exception),
            error_code=exception.error_code,
        )
    except ExternalAPIUnreachableException as exception:
        raise HTTPError(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            error_message=str(exception),
            error_code=exception.error_code,
        )
