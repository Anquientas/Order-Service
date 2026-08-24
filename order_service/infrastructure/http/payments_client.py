import httpx

from order_service.domain.entities import Payment


class HttpPaymentsClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 5.0,
    ) -> None:
        self._http = httpx.AsyncClient(
            base_url=base_url.rstrip('/'),
            headers={'X-API-Key': api_key},
            timeout=timeout,
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def create_payment(
        self,
        order_id: str,
        amount: str,
        callback_url: str,
        idempotency_key: str,
    ) -> Payment | None:
        try:
            response = await self._http.post(
                '/api/payments',
                json={
                    'order_id': order_id,
                    'amount': amount,
                    'callback_url': callback_url,
                    'idempotency_key': idempotency_key,
                },
            )
        except httpx.HTTPError:
            return None

        if response.status_code not in (200, 201):
            return None

        try:
            data = response.json()
            return Payment(
                id=data['id'],
                order_id=data['order_id'],
                status=data['status'],
            )
        except (ValueError, KeyError):
            return None
