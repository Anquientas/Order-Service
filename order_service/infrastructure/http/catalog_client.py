import httpx

from order_service.domain.entities import CatalogItem
from order_service.domain.exceptions import CatalogServiceUnavailable


class HttpCatalogClient:
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

    async def get_item(self, item_id: str) -> CatalogItem | None:
        try:
            response = await self._http.get(f'/api/catalog/items/{item_id}')
        except httpx.HTTPError as exception:
            raise CatalogServiceUnavailable(
                f'Catalog Service недоступен: {exception}'
            ) from exception

        if response.status_code == 404:
            return None

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exception:
            raise CatalogServiceUnavailable(
                f'Catalog Service вернул {response.status_code}: '
                f'{response.text[:300]}'
            ) from exception

        data = response.json()
        return CatalogItem(
            id=data['id'],
            available_qty=data['available_qty'],
        )
