from enum import StrEnum


class OrderStatus(StrEnum):
    new = 'NEW'
    paid = 'PAID'
    shipped = 'SHIPPED'
    cancelled = 'CANCELLED'
