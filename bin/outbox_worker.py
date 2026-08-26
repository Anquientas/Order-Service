import asyncio
import logging
import signal

from order_service.bootstrap import (
    start_background_workers,
    stop_background_workers,
)
from order_service.constants.log_messages import OutboxWorkerLogMessage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
)

logger = logging.getLogger(__name__)


async def main() -> None:
    await start_background_workers()
    logger.info(OutboxWorkerLogMessage.started)

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()
    logger.info(OutboxWorkerLogMessage.shutting_down)
    await stop_background_workers()
    logger.info(OutboxWorkerLogMessage.stopped)


if __name__ == '__main__':
    asyncio.run(main())
