from typing import Protocol


class GatewayRatelimiterProto(Protocol):
    def __init__(self, rate: int, per: int) -> None:
        ...

    async def acquire(self) -> None:
        ...
