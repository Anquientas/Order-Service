from typing import Protocol

from order_service.domain.entities import NotificationOutboxRecord


class NotificationOutboxRepository(Protocol):
    async def enqueue(self, record: NotificationOutboxRecord) -> None: ...

    async def get_pending(
        self, limit: int
    ) -> list[NotificationOutboxRecord]: ...

    async def mark_sent(self, record_id: str) -> None: ...

    async def mark_retry(self, record_id: str, error: str) -> None: ...

    async def mark_permanently_failed(
        self, record_id: str, error: str
    ) -> None: ...
