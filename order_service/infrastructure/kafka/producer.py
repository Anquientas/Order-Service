import json

from aiokafka import AIOKafkaProducer


class KafkaEventPublisher:
    def __init__(self, bootstrap_servers: str) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
        )
        await self._producer.start()

    async def stop(self) -> None:
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None

    async def publish(
        self, topic: str, payload: dict, key: str | None = None
    ) -> None:
        assert self._producer is not None
        await self._producer.send_and_wait(
            topic,
            value=json.dumps(payload).encode('utf-8'),
            key=key.encode('utf-8') if key is not None else None,
        )
