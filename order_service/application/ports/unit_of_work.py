from types import TracebackType
from typing import Protocol

from order_service.application.ports.order_repository import OrderRepository


class UnitOfWork(Protocol):
    orders: OrderRepository

    async def __aenter__(self) -> 'UnitOfWork': ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
