from asyncio import Future, TimeoutError, create_task, sleep, wait_for
from typing import Awaitable, Callable, Type

from orx.proto.gateway import GatewayRatelimiterProto, ShardProto
from orx.proto.http import ClientProto
from orx.impl.http import Route

from .ratelimiter import GatewayRatelimiter
from .shard import Shard


class GatewayClient:
    def __init__(
        self,
        token: str,
        intents: int,
        http: ClientProto,
        ratelimiter_cls: Type[GatewayRatelimiterProto] = None,
        shard_cls: Type[ShardProto] = None,
        shard_ids: list[int] = None,
        shard_count: int = None,
    ) -> None:
        self.shards: dict[int, ShardProto] = {}

        self._shard_ids = shard_ids
        self._shard_count = shard_count

        if shard_ids and not shard_count:
            raise ValueError("shard_count must be set if shard_ids is set")

        self._hooks: dict[str, list[Callable[..., Awaitable[None]]]] = {}

        self._token = token
        self._intents = intents
        self._http = http

        self._ratelimiter_cls = ratelimiter_cls or GatewayRatelimiter
        self._shard_cls = shard_cls or Shard

    def add_dispatch_hook(self, event: str, hook: Callable[..., Awaitable[None]]) -> None:
        if event not in self._hooks:
            self._hooks[event] = [hook]
            return
        self._hooks[event].append(hook)

    def get_shard(self, id: int) -> ShardProto:
        return self.shards[id]

    async def start(self) -> None:
        response = await self._http.request(Route("GET", "/gateway/bot"))
        data = await response.json()

        ssl = data["session_start_limit"]

        start_limiter = self._ratelimiter_cls(ssl["max_concurrency"], 5)

        shard_count = 0

        if not self._shard_ids:
            if self._shard_count:
                self._shard_ids = list(range(self._shard_count))
            else:
                shard_count: int = data["shards"]
                self._shard_ids = list(range(shard_count))

        for shard_id in self._shard_ids:
            shard = self._shard_cls(
                shard_id,
                self._shard_count or shard_count,
                self._http,
                self._token,
                self._intents,
                self._ratelimiter_cls,
            )
            self.shards[shard_id] = shard

            shard.callbacks = self._hooks

            await start_limiter.acquire()
            await sleep(1.75)

            create_task(shard.connect())

            try:
                await wait_for(shard.ready.wait(), timeout=5)
            except TimeoutError:
                pass

        fut = Future()

        await fut

    async def close(self) -> None:
        for shard in self.shards.values():
            await shard.close()
