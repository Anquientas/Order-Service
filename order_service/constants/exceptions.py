from enum import StrEnum


class OrderExceptionMessage(StrEnum):
    order_not_found = 'Order {order_id!r} not found'
    duplicate_idempotency_key = (
        'Order with idempotency_key {idempotency_key!r} already exists'
    )


class CatalogExceptionMessage(StrEnum):
    item_not_found = 'Item {item_id!r} not found in catalog'
    insufficient_stock = (
        'Item {item_id!r}: requested {requested}, available {available}'
    )
    service_unreachable = 'Catalog Service недоступен: {exception}'
    service_rejected = 'Catalog Service вернул {status_code}: {body}'
