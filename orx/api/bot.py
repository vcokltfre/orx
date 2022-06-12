from typing import Type

from orx.impl.gateway import GatewayClient
from orx.impl.http import HTTPClient
from orx.proto.gateway import GatewayClientProto
from orx.proto.http import HTTPClientProto


class Bot:
    def __init__(
        self,
        token: str,
        intents: int,
        *,
        http_cls: Type[HTTPClientProto] = HTTPClient,
        gateway_cls: Type[GatewayClientProto] = GatewayClient,
    ) -> None:
        self._http = http_cls(token)
        self._gateway = gateway_cls(token, intents, self._http)

    async def start(self) -> None:
        await self._gateway.start(wait=False, fail_early=True)

    async def stop(self) -> None:
        await self._gateway.close()
        await self._http.close()

    async def __aenter__(self) -> "Bot":
        await self.start()
        return self

    async def __aexit__(self, exc_type: Type[BaseException], exc_val: BaseException, exc_tb: BaseException) -> None:
        await self.stop()
