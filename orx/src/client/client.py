from sys import stdout

from loguru import logger

from orx.objects.state import ConnectionState
from orx.objects.user import User

from .options import Options

logger.configure(handlers=[{"sink": stdout, "level": "INFO"}])


class OrxClient:
    def __init__(
        self,
        token: str,
        intents: int,
        shard_ids: list[int] = None,
        shard_count: int = None,
        options: Options = None,
    ) -> None:
        options = options or Options()

        self._http = options.http_cls(
            token,
            options.api_url,
            options.headers,
            options.http_retries,
            options.http_ratelimiter,
        )
        self._gateway = options.gateway_cls(
            token,
            intents,
            self._http,
            options.gateway_ratelimiter,
            options.shard_cls,
            shard_ids,
            shard_count,
        )

        self._state = ConnectionState(self._http, self._gateway)

    def on(self, event: str):
        def decorator(func):
            self._gateway.add_dispatch_hook(event.upper(), func)
            return func

        return decorator

    async def start(self) -> None:
        await self._gateway.start()

    async def me(self) -> User:
        return await User.me(self._state)
