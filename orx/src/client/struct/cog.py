from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable

if TYPE_CHECKING:
    from orx import OrxClient


Callback = Callable[..., Awaitable[None]]


class Cog:
    def __init__(self, client: OrxClient, *, name: str = None) -> None:
        self._client = client
        self.name = name or self.__class__.__name__

        for attr in dir(self):
            _attr = getattr(self, attr)

            if ls := getattr(_attr, "__listener__", None):
                self._client.on(ls)(_attr)

    @staticmethod
    def listener(event: str = None) -> Callable[[Callback], Callback]:
        def deco(func: Callback) -> Callback:
            func.__listener__ = event or func.__name__.removeprefix("on_")
            return func

        return deco

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} name={self.name}>"

    async def __load__(self) -> None:
        pass

    async def __unload__(self) -> None:
        pass
