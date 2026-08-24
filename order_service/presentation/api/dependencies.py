from fastapi import Depends
from order_service.application.ports.catalog_client import CatalogClient
from order_service.application.ports.payments_client import PaymentsClient
from order_service.application.ports.unit_of_work import UnitOfWork
from order_service.application.usecases.create_order import (
    CreateOrderUsecase,
)
from order_service.application.usecases.get_order import GetOrderUsecase
from order_service.application.usecases.process_payment_callback import (
    ProcessPaymentCallbackUsecase,
)
from order_service.infrastructure.http.catalog_client import (
    HttpCatalogClient,
)
from order_service.infrastructure.http.payments_client import (
    HttpPaymentsClient,
)
from order_service.infrastructure.persistence.database import SessionFactory
from order_service.infrastructure.persistence.unit_of_work import (
    SqlAlchemyUnitOfWork,
)
from order_service.settings import settings

_catalog_client = HttpCatalogClient(
    base_url=settings.capashino.base_url,
    api_key=settings.capashino.api_secret_key,
)

_payments_client = HttpPaymentsClient(
    base_url=settings.capashino.base_url,
    api_key=settings.capashino.api_secret_key,
)

_callback_url = (
    f'{settings.ORDER_SERVICE_CALLBACK_BASE_URL.rstrip("/")}'
    f'/api/orders/payment-callback'
)


def get_unit_of_work() -> UnitOfWork:
    return SqlAlchemyUnitOfWork(SessionFactory)


def get_catalog_client() -> CatalogClient:
    return _catalog_client


def get_payments_client() -> PaymentsClient:
    return _payments_client


def get_create_order_usecase(
    uow: UnitOfWork = Depends(get_unit_of_work),
    catalog: CatalogClient = Depends(get_catalog_client),
    payments: PaymentsClient = Depends(get_payments_client),
) -> CreateOrderUsecase:
    return CreateOrderUsecase(
        uow=uow,
        catalog=catalog,
        payments=payments,
        callback_url=_callback_url,
    )


def get_get_order_usecase(
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> GetOrderUsecase:
    return GetOrderUsecase(uow=uow)


def get_process_payment_callback_usecase(
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> ProcessPaymentCallbackUsecase:
    return ProcessPaymentCallbackUsecase(uow=uow)


async def close_http_clients() -> None:
    await _catalog_client.aclose()
    await _payments_client.aclose()
