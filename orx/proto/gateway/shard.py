from asyncio import Event
from typing import Any, Callable, Coroutine, Protocol, Type

from orx.proto.http import ClientProto
from orx.utils import JSON

from .ratelimiter import GatewayRatelimiterProto


class ShardProto(Protocol):
    id: int
    latency: float | None
    callbacks: dict[str, list[Callable[..., Coroutine[Any, Any, None]]]]
    ready: Event

    def __init__(
        self,
        id: int,
        shard_count: int,
        http: ClientProto,
        token: str,
        intents: int,
        ratelimiter_cls: Type[GatewayRatelimiterProto],
    ) -> None:
        ...

    async def connect(self) -> None:
        ...

    async def close(self) -> None:
        ...

    async def send(self, data: dict[str, JSON]) -> None:
        ...
