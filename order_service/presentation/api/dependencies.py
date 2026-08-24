from collections.abc import AsyncIterator

from fastapi import Depends
from order_service.application.ports.catalog_client import CatalogClient
from order_service.application.ports.unit_of_work import UnitOfWork
from order_service.application.usecases.create_order import (
    CreateOrderUsecase,
)
from order_service.application.usecases.get_order import GetOrderUsecase
from order_service.infrastructure.http.catalog_client import (
    HttpCatalogClient,
)
from order_service.infrastructure.persistence.database import SessionFactory
from order_service.infrastructure.persistence.unit_of_work import (
    SqlAlchemyUnitOfWork,
)
from order_service.settings import settings

_capashino_client = HttpCatalogClient(
    base_url=settings.capashino.base_url,
    api_key=settings.capashino.api_secret_key,
)


def get_unit_of_work() -> UnitOfWork:
    return SqlAlchemyUnitOfWork(SessionFactory)


def get_catalog_client() -> CatalogClient:
    return _capashino_client


def get_create_order_usecase(
    uow: UnitOfWork = Depends(get_unit_of_work),
    catalog: CatalogClient = Depends(get_catalog_client),
) -> CreateOrderUsecase:
    return CreateOrderUsecase(uow=uow, catalog=catalog)


def get_get_order_usecase(
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> GetOrderUsecase:
    return GetOrderUsecase(uow=uow)


async def close_catalog_client() -> AsyncIterator[None]:
    yield
    await _capashino_client.aclose()
