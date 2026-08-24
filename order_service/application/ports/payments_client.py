from typing import Protocol

from order_service.domain.entities import Payment


class PaymentsClient(Protocol):
    async def create_payment(
        self,
        order_id: str,
        amount: str,
        callback_url: str,
        idempotency_key: str,
    ) -> Payment | None: ...
