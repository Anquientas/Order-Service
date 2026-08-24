import datetime

from pydantic import BaseModel, Field

from order_service.constants.payment import PaymentStatus


class CreateOrderRequest(BaseModel):
    user_id: str
    quantity: int = Field(gt=0)
    item_id: str
    idempotency_key: str | None = Field(default=None, max_length=128)


class OrderResponse(BaseModel):
    id: str
    user_id: str
    quantity: int
    item_id: str
    status: str
    created_at: datetime.datetime
    update_at: datetime.datetime


class PaymentCallbackRequest(BaseModel):
    payment_id: str
    order_id: str
    status: PaymentStatus
    amount: str
    error_message: str | None = None
