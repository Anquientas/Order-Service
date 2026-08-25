from types import TracebackType
from typing import Protocol

from order_service.application.ports.inbox_repository import InboxRepository
from order_service.application.ports.notification_outbox_repository import (
    NotificationOutboxRepository,
)
from order_service.application.ports.order_repository import OrderRepository
from order_service.application.ports.outbox_repository import (
    OutboxRepository,
)


class UnitOfWork(Protocol):
    orders: OrderRepository
    outbox: OutboxRepository
    inbox: InboxRepository
    notification_outbox: NotificationOutboxRepository

    async def __aenter__(self) -> 'UnitOfWork': ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
