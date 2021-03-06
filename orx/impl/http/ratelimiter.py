from asyncio import Event, Lock, create_task, sleep
from typing import Type

from orx.proto.http import BucketProto


class Bucket:
    __slots__ = (
        "_rate",
        "_per",
        "_lock",
        "_deferred",
    )

    def __init__(self, rate: int, per: int) -> None:
        """A ratelimiting bucket.

        Args:
            rate (int): The number of requests allowed within a period.
            per (int): The period of the bucket.
        """

        self._rate = rate
        self._per = per

        self._deferred = False

        self._lock = Lock()

    async def __aenter__(self) -> "Bucket":
        await self._lock.acquire()
        return self

    async def __aexit__(self, exc_type: Type[BaseException], exc_val: BaseException, exc_tb: BaseException) -> None:
        if not self._deferred:
            self._lock.release()

    async def _unlock(self, after: float) -> None:
        await sleep(after)

        self._lock.release()
        self._deferred = False

    async def set_rate(self, rate: int, per: int) -> None:
        """Set the rate of the bucket.

        Args:
            rate (int): The new number of requests allowed within a period.
            per (int): The new period of the bucket.
        """

        self._rate = rate
        self._per = per

    async def defer(self, unlock_after: float) -> None:
        """Defer unlocking the bucket for a set period.

        Args:
            unlock_after (float): After how many seconds to unlock the bucket.
        """

        self._deferred = True
        create_task(self._unlock(unlock_after))


class Ratelimiter:
    __slots__ = (
        "_buckets",
        "_global",
    )

    def __init__(self) -> None:
        """A ratelimiter for HTTP requests."""

        self._buckets: dict[str, BucketProto] = {}

        self._global = Event()
        self._global.set()

    async def acquire(self, bucket: str) -> BucketProto:
        """Acquire a ratelimit lock on a given bucket.

        Args:
            bucket (str): The bucket to acquire the lock on.

        Returns:
            BucketProto: The acquired bucket.
        """

        if bucket not in self._buckets:
            self._buckets[bucket] = Bucket(rate=1, per=1)
        return self._buckets[bucket]

    async def _unlock_global(self, after: float) -> None:
        await sleep(after)
        self._global.set()

    async def set_global_lock(self, unlock_after: float) -> None:
        """Set the global lock after hitting the global limit.

        Args:
            unlock_after (float): After how many seconds to unlock the global lock.

        Raises:
            RuntimeError: The global lock is already locked.
        """

        if not self._global.is_set():
            raise RuntimeError("Global lock is already locked.")

        self._global.clear()
        create_task(self._unlock_global(unlock_after))
