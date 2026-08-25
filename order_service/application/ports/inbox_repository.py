from typing import Protocol


class InboxRepository(Protocol):
    async def is_processed(
        self, topic: str, partition: int, offset: int
    ) -> bool: ...

    async def mark_processed(
        self, topic: str, partition: int, offset: int
    ) -> None: ...
