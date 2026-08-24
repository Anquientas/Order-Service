class OrderNotFound(Exception):
    def __init__(self, order_id: str) -> None:
        super().__init__(f'Order {order_id!r} not found')
        self.order_id = order_id


class ItemNotFound(Exception):
    def __init__(self, item_id: str) -> None:
        super().__init__(f'Item {item_id!r} not found in catalog')
        self.item_id = item_id


class InsufficientStock(Exception):
    def __init__(self, item_id: str, requested: int, available: int) -> None:
        super().__init__(
            f'Item {item_id!r}: requested {requested}, available {available}'
        )
        self.item_id = item_id
        self.requested = requested
        self.available = available


class CatalogServiceUnavailable(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
