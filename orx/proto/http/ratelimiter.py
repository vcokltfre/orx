from typing import Protocol, Type


class BucketProto(Protocol):
    def __init__(self, rate: int, per: int) -> None:
        ...

    async def __aenter__(self) -> "BucketProto":
        ...

    async def __aexit__(self, exc_type: Type[BaseException], exc_val: BaseException, exc_tb: BaseException) -> None:
        ...

    async def set_rate(self, rate: int, per: int) -> None:
        ...

    async def defer(self, unlock_after: float) -> None:
        ...


class RatelimiterProto(Protocol):
    async def acquire(self, bucket: str) -> BucketProto:
        ...

    async def set_global_lock(self, unlock_after: float) -> None:
        ...
