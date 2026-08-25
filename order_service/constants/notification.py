from enum import StrEnum


class NotificationMessage(StrEnum):
    order_new = 'Ваш заказ создан и ожидает оплаты'
    order_paid = 'Ваш заказ успешно оплачен и готов к отправке'
    order_shipped = 'Ваш заказ отправлен в доставку'
    order_cancelled = 'Ваш заказ отменен. Причина: {reason}'


class NotificationIdempotencyKey(StrEnum):
    order_new = 'order-created:{order_id}'
    order_paid = 'order-paid:{order_id}'
    order_shipped = 'order-shipped:{order_id}'
    order_cancelled = 'order-cancelled:{order_id}'


class DefaultCancellationReason(StrEnum):
    payment_not_created = 'Не удалось создать платёж'
    payment_failed = 'Оплата не прошла'
    shipment_cancelled = 'Недостаточно товара на складе'
