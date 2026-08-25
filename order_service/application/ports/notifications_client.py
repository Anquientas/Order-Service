from typing import Protocol


class NotificationsClient(Protocol):
    async def send(
        self, message: str, reference_id: str, idempotency_key: str
    ) -> None: ...
