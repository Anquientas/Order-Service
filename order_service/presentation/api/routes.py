from fastapi import APIRouter, Depends, HTTPException, status
from order_service.application.usecases.create_order import (
    CreateOrderUsecase,
)
from order_service.application.usecases.get_order import GetOrderUsecase
from order_service.application.usecases.process_payment_callback import (
    ProcessPaymentCallbackUsecase,
)
from order_service.domain.entities import Order
from order_service.domain.exceptions import (
    CatalogServiceUnavailable,
    InsufficientStock,
    ItemNotFound,
    OrderNotFound,
)
from order_service.presentation.api.dependencies import (
    get_create_order_usecase,
    get_get_order_usecase,
    get_process_payment_callback_usecase,
)
from order_service.presentation.api.schemas import (
    CreateOrderRequest,
    OrderResponse,
    PaymentCallbackRequest,
)

router = APIRouter(prefix='/api/orders', tags=['orders'])


def _to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        quantity=order.quantity,
        item_id=order.item_id,
        status=order.status,
        created_at=order.created_at,
        update_at=order.updated_at,
    )


@router.post(
    '',
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    payload: CreateOrderRequest,
    usecase: CreateOrderUsecase = Depends(get_create_order_usecase),
) -> OrderResponse:
    try:
        order = await usecase.execute(
            user_id=payload.user_id,
            item_id=payload.item_id,
            quantity=payload.quantity,
            idempotency_key=payload.idempotency_key,
        )
    except (ItemNotFound, InsufficientStock) as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exception)
        ) from exception
    except CatalogServiceUnavailable as exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exception)
        ) from exception
    return _to_response(order)


@router.get('/{order_id}', response_model=OrderResponse)
async def get_order(
    order_id: str,
    usecase: GetOrderUsecase = Depends(get_get_order_usecase),
) -> OrderResponse:
    try:
        order = await usecase.execute(order_id)
    except OrderNotFound as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exception)
        ) from exception
    return _to_response(order)


@router.post('/payment-callback', status_code=status.HTTP_200_OK)
async def payment_callback(
    payload: PaymentCallbackRequest,
    usecase: ProcessPaymentCallbackUsecase = Depends(
        get_process_payment_callback_usecase
    ),
) -> dict[str, str]:
    await usecase.execute(
        order_id=payload.order_id,
        payment_id=payload.payment_id,
        status=payload.status,
        error_message=payload.error_message,
    )
    return {'status': 'ok'}
