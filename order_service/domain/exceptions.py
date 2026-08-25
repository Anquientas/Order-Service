from order_service.constants.exceptions import (
    CatalogExceptionMessage,
    OrderExceptionMessage,
)


class OrderNotFound(Exception):
    def __init__(self, order_id: str) -> None:
        super().__init__(
            OrderExceptionMessage.order_not_found.format(order_id=order_id)
        )
        self.order_id = order_id


class DuplicateIdempotencyKey(Exception):
    def __init__(self, idempotency_key: str) -> None:
        super().__init__(
            OrderExceptionMessage.duplicate_idempotency_key.format(
                idempotency_key=idempotency_key
            )
        )
        self.idempotency_key = idempotency_key


class ItemNotFound(Exception):
    def __init__(self, item_id: str) -> None:
        super().__init__(
            CatalogExceptionMessage.item_not_found.format(item_id=item_id)
        )
        self.item_id = item_id


class InsufficientStock(Exception):
    def __init__(self, item_id: str, requested: int, available: int) -> None:
        super().__init__(
            CatalogExceptionMessage.insufficient_stock.format(
                item_id=item_id, requested=requested, available=available
            )
        )
        self.item_id = item_id
        self.requested = requested
        self.available = available


class CatalogServiceUnavailable(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
