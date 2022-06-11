from asyncio import Semaphore, create_task, sleep


class GatewayRatelimiter:
    def __init__(self, rate: int, per: int) -> None:
        """A gateway rate limiter implementation.

        Args:
            rate (int): The rate at which payloads can be sent.
            per (int): The interval at which the limit clears.
        """

        self._per = per
        self._lock = Semaphore(rate)

    async def _release(self, after: float) -> None:
        await sleep(after)
        self._lock.release()

    async def acquire(self) -> None:
        """Acquire a ratelimit lock."""

        await self._lock.acquire()

        create_task(self._release(self._per))
