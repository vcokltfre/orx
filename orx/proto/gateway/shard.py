from asyncio import Event
from typing import Any, Callable, Coroutine, Protocol, Type, Union

from discord_typings.gateway import (
    HeartbeatCommand,
    IdentifyCommand,
    RequestGuildMembersCommand,
    ResumeCommand,
    UpdatePresenceCommand,
    VoiceUpdateCommand,
)

from ..http import HTTPClientProto
from .ratelimiter import GatewayRatelimiterProto

Command = Union[
    ResumeCommand,
    IdentifyCommand,
    HeartbeatCommand,
    VoiceUpdateCommand,
    UpdatePresenceCommand,
    RequestGuildMembersCommand,
]


class ShardProto(Protocol):
    id: int
    latency: float | None
    callbacks: dict[str, list[Callable[..., Coroutine[Any, Any, None]]]]
    ready: Event

    def __init__(
        self,
        id: int,
        shard_count: int,
        token: str,
        intents: int,
        ratelimiter_cls: Type[GatewayRatelimiterProto],
    ) -> None:
        ...

    async def connect(self, url: str, http: HTTPClientProto) -> None:
        ...

    async def close(self) -> None:
        ...

    async def send(self, data: Command) -> None:
        ...
