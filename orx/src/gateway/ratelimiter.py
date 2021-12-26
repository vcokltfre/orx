from asyncio import Semaphore, create_task, sleep


class GatewayRatelimiter:
    def __init__(self, rate: int, per: int) -> None:
        self._per = per
        self._lock = Semaphore(rate)

    async def _release(self, after: float) -> None:
        await sleep(after)
        self._lock.release()

    async def acquire(self) -> None:
        await self._lock.acquire()

        create_task(self._release(self._per))
