from typing import Protocol


class BucketProto(Protocol):
    def __init__(self, rate: int, per: int) -> None:
        ...

    async def __aenter__(self) -> "BucketProto":
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        ...

    async def set_rate(self, rate: int, per: int) -> None:
        ...

    async def defer(self, unlock_after: float) -> None:
        ...


class RatelimiterProto(Protocol):
    async def acquire(self, bucket: str) -> BucketProto:
        ...

    async def set_global_lock(self, unlock_after: float) -> None:
        pass
