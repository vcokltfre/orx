from typing import Any, Callable, Coroutine, Optional, Protocol, Type

from orx.proto.http import HTTPClientProto

from .ratelimiter import GatewayRatelimiterProto
from .shard import ShardProto


class GatewayClientProto(Protocol):
    shards: dict[int, ShardProto]

    def __init__(
        self,
        token: str,
        intents: int,
        http: HTTPClientProto,
        ratelimiter_cls: Optional[Type[GatewayRatelimiterProto]] = None,
        shard_cls: Optional[Type[ShardProto]] = None,
        shard_ids: Optional[list[int]] = None,
        shard_count: Optional[int] = None,
    ) -> None:
        ...

    def add_dispatch_hook(self, event: str, hook: Callable[..., Coroutine[Any, Any, None]]) -> None:
        ...

    def get_shard(self, id: int) -> ShardProto:
        ...

    async def start(self) -> None:
        ...

    async def close(self) -> None:
        ...
