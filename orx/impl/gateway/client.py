from asyncio import Future, Task, create_task
from typing import Any, Callable, Coroutine, Optional, Type, TypedDict

from orx.impl.http import Route
from orx.proto.gateway import GatewayRatelimiterProto, ShardProto
from orx.proto.http import HTTPClientProto

from .ratelimiter import GatewayRatelimiter
from .shard import Shard


class SessionStartLimit(TypedDict):
    total: int
    remaining: int
    reset_after: int
    max_concurrency: int


class GetGatewayBot(TypedDict):
    url: str
    shards: int
    session_start_limit: SessionStartLimit


class GatewayClient:
    __slots__ = (
        "shards",
        "_shard_tasks",
        "_shard_ids",
        "_shard_count",
        "_hooks",
        "_token",
        "_intents",
        "_http",
        "_ratelimiter_cls",
        "_shard_cls",
        "_done",
    )

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
        self.shards: dict[int, ShardProto] = {}
        self._shard_tasks: dict[int, Task[None]] = {}

        self._shard_ids = shard_ids
        self._shard_count = shard_count

        if shard_ids and not shard_count:
            raise ValueError("shard_count must be set if shard_ids is set")

        self._hooks: dict[str, list[Callable[..., Coroutine[Any, Any, None]]]] = {}

        self._token = token
        self._intents = intents
        self._http = http

        self._ratelimiter_cls = ratelimiter_cls or GatewayRatelimiter
        self._shard_cls = shard_cls or Shard

        self._done = Future[None]()

    async def _get_gateway(self) -> GetGatewayBot:
        route = Route("GET", "/gateway/bot")
        response = await self._http.request(route)

        data = await response.json()

        return data

    def add_dispatch_hook(self, event: str, hook: Callable[..., Coroutine[Any, Any, None]]) -> None:
        if event not in self._hooks:
            self._hooks[event] = [hook]
            return
        self._hooks[event].append(hook)

    def get_shard(self, id: int) -> ShardProto:
        return self.shards[id]

    async def start(self, *, fail_early: bool = False, wait: bool = True) -> None:
        gateway = await self._get_gateway()
        session_limits = gateway["session_start_limit"]

        if not self._shard_ids:
            if self._shard_count:
                self._shard_ids = list(range(self._shard_count))
            else:
                self._shard_count = gateway["shards"]
                self._shard_ids = list(range(self._shard_count))

        if fail_early and session_limits["remaining"] < len(self._shard_ids):
            raise RuntimeError("Insufficient remaining identify calls to start shards.")

        if not self._shard_count:
            raise RuntimeError("shard_count is not set while starting shards")

        limiter = self._ratelimiter_cls(session_limits["max_concurrency"], 5)
        last_shard: Optional[ShardProto] = None

        for shard_id in self._shard_ids:
            shard = self._shard_cls(
                shard_id,
                self._shard_count,
                self._token,
                self._intents,
                self._ratelimiter_cls,
            )

            shard.callbacks.update(self._hooks)
            self.shards[shard_id] = shard

            await limiter.acquire()

            if last_shard:
                await last_shard.ready.wait()

            last_shard = shard

            self._shard_tasks[shard.id] = create_task(shard.connect(gateway["url"], self._http))

        if wait:
            await self._done

    async def close(self) -> None:
        for shard in self.shards.values():
            await shard.close()

        self._done.set_result(None)

    async def __aenter__(self) -> "GatewayClient":
        await self.start()
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()
