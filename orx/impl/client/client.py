from sys import stdout
from typing import Type

from loguru import logger

from orx.objects.state import ConnectionState
from orx.objects.user import User

from .options import Options
from .resolver import Resolver
from .struct import Cog

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
        """A high level client for connecting to the Discord API.

        Args:
            token (str): The bot token to connect with.
            intents (int): The gateway intents to connect with.
            shard_ids (list[int], optional): The shard IDs to use. Defaults to None.
            shard_count (int, optional): The number of shards in the shard group. Defaults to None.
            options (Options, optional): Advancaed library configuration options. Defaults to None.
        """

        options = options or Options()

        self.resolver = Resolver()

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

        self._cogs: set[Cog] = set()
        self._state = ConnectionState(self._http, self.resolver, self._gateway)

    def on(self, event: str):
        """Listen for an event from the gateway.

        Note: this will deliver raw events from the gateway, not parsed data.

        Args:
            event (str): The event to listen for. Use '*' to listen for all events.
        """

        def decorator(func):
            self._gateway.add_dispatch_hook(event.upper(), func)
            return func

        return decorator

    def add_cog(self, cog: Type[Cog] | Cog, *args, **kwargs) -> None:
        if isinstance(cog, Cog):
            self._cogs.add(cog)
            return
        self._cogs.add(cog(self, *args, **kwargs))

    async def start(self) -> None:
        """
        Start the client connecting to the gateway.
        """

        for cog in self._cogs:
            await cog.__load__()

        await self._gateway.start()

    async def me(self) -> User:
        """
        Get the currently authenticated user.
        """

        return await User.me(self._state)
