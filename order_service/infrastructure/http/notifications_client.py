import httpx


class HttpNotificationsClient:
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

    async def send(
        self, message: str, reference_id: str, idempotency_key: str
    ) -> None:
        response = await self._http.post(
            '/api/notifications',
            json={
                'message': message,
                'reference_id': reference_id,
                'idempotency_key': idempotency_key,
            },
        )
        response.raise_for_status()
