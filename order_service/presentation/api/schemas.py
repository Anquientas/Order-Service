import datetime

from pydantic import BaseModel, Field


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
