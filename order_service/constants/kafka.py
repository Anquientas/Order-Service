from enum import StrEnum

from order_service.constants.order import OrderStatus


class EventTopic(StrEnum):
    order = 'student_system-order.events'
    shipment = 'student_system-shipment.events'


class OrderEventType(StrEnum):
    paid = 'order.paid'


class ShipmentEventType(StrEnum):
    shipped = 'order.shipped'
    cancelled = 'order.cancelled'


SHIPMENT_EVENT_TO_ORDER_STATUS: dict[ShipmentEventType, OrderStatus] = {
    ShipmentEventType.shipped: OrderStatus.shipped,
    ShipmentEventType.cancelled: OrderStatus.cancelled,
}
