from typing import Protocol

from order_service.domain.entities import CatalogItem


class CatalogClient(Protocol):
    """Интерфейс запроса в Catalog Service."""

    async def get_item(self, item_id: str) -> CatalogItem | None: ...
