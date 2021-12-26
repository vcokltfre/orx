from typing import Awaitable, Callable, Protocol, Type

from orx.proto.http import ClientProto

from .ratelimiter import GatewayRatelimiterProto
from .shard import ShardProto


class GatewayClientProto(Protocol):
    shards: list[ShardProto]

    def __init__(
        self,
        token: str,
        intents: int,
        http: ClientProto,
        ratelimiter_cls: Type[GatewayRatelimiterProto],
        shard_cls: Type[ShardProto],
    ) -> None:
        ...

    def add_dispatch_hook(self, event: str, hook: Callable[..., Awaitable[None]]) -> None:
        ...

    def get_shard(self, id: int) -> ShardProto:
        ...

    async def start(self) -> None:
        ...