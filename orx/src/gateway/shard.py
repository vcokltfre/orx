from asyncio import Event, Task, create_task, sleep
from random import randrange
from sys import platform
from time import time
from typing import Awaitable, Callable, Type

from aiohttp import ClientWebSocketResponse, WSMessage, WSMsgType

from orx.errors import GatewayCriticalError, GatewayReconnect
from orx.proto.gateway import GatewayRatelimiterProto
from orx.proto.http import ClientProto
from orx.src.http import Route
from orx.utils import JSON

from .enums import GatewayCloseCodes, GatewayOps
from .event import EventDirection, GatewayEvent
from .ratelimiter import GatewayRatelimiter

CRITICAL = [
    GatewayCloseCodes.NOT_AUTHENTICATED,
    GatewayCloseCodes.AUTHENTICATION_FAILED,
    GatewayCloseCodes.INVALID_API_VERSION,
    GatewayCloseCodes.INVALID_INTENTS,
    GatewayCloseCodes.DISALLOWED_INTENTS,
]

NONCRITICAL = [
    GatewayCloseCodes.INVALID_SEQ,
    GatewayCloseCodes.RATE_LIMITED,
    GatewayCloseCodes.SESSION_TIMEOUT,
]


class Shard:
    def __init__(
        self,
        id: int,
        shard_count: int,
        http: ClientProto,
        token: str,
        intents: int,
        ratelimiter_cls: Type[GatewayRatelimiterProto] = GatewayRatelimiter,
    ) -> None:
        self.id = id
        self.callbacks: dict[str, list[Callable[..., Awaitable[None]]]] = {}

        self.ready = Event()
        self.ready.clear()

        self._count = shard_count
        self._http = http
        self._token = token
        self._intents = intents

        self._ratelimiter = ratelimiter_cls(120, 60)

        self._session: str | None = None
        self._seq: int | None = None

        self._url: str | None = None
        self._ws: ClientWebSocketResponse | None = None

        self._pacemaker: Task | None = None
        self._last_hb: float | None = None
        self._last_ack: float | None = None

        self._closing = False

        self.latency: float | None = None

    def __repr__(self) -> str:
        return f"<Shard id={self.id} seq={self._seq}>"

    async def connect(self) -> None:
        while True:
            if not self._url:
                response = await self._http.request(Route("GET", "/gateway"))
                data = await response.json()

                self._url = data["url"]

            if self._ws and not self._ws.closed:
                await self._ws.close()

            self._ws = await self._http.ws_connect(self._url)

            if self._session:
                await self._resume()

            try:
                await self._read()
            except GatewayReconnect:
                pass

            if self._closing:
                return

    async def close(self, final: bool = False) -> None:
        if final:
            self.closing = True

        if self._ws and not self._ws.closed:
            await self._ws.close()

        if self._pacemaker and not self._pacemaker.cancelled():
            self._pacemaker.cancel()

    async def send(self, data: dict[str, JSON]) -> None:
        await self._ratelimiter.acquire()

        if not self._ws:
            raise Exception("Shard is not connected to the gateway while trying to send data")

        event = GatewayEvent(self, EventDirection.OUTGOING, data, **data)  # type: ignore

        self._callback(event)

        try:
            await self._ws.send_json(data)
        except OSError:
            await self.close()
        except Exception:
            await self.close()
            raise

    def _callback(self, event: GatewayEvent) -> None:
        for callback in self.callbacks.get(event.dispatch_name, []):
            create_task(callback(event))

        for callback in self.callbacks.get("*", []):
            create_task(callback(event))

    async def _identify(self) -> None:
        await self.send(
            {
                "op": GatewayOps.IDENTIFY,
                "d": {
                    "token": self._token,
                    "properties": {
                        "$os": platform,
                        "$browser": "Orx",
                        "$device": "Orx",
                    },
                    "intents": self._intents,
                    "shard": [self.id, self._count],
                },
            }
        )

    async def _resume(self) -> None:
        await self.send(
            {
                "op": GatewayOps.RESUME,
                "d": {
                    "token": self._token,
                    "session_id": self._session,
                    "seq": self._seq,
                },
            }
        )

    async def _handle_disconnect(self, code: int) -> None:
        """Handle the gateway disconnecting correctly."""

        if code in CRITICAL:
            raise GatewayCriticalError(code)

        if code in NONCRITICAL:
            self._session = None
            self._seq = None

        await self.close()

        raise GatewayReconnect()

    async def _dispatch(self, data: dict) -> None:
        event = GatewayEvent(self, EventDirection.INCOMING, data, **data)

        self._callback(event)

        if event.op == GatewayOps.HELLO:
            self._pacemaker = create_task(self._heartbeat(data["d"]["heartbeat_interval"]))
            await self._identify()
        elif event.op == GatewayOps.ACK:
            self._last_ack = time()
        elif event.op == GatewayOps.RECONNECT:
            await self.close()
            raise GatewayReconnect()
        elif event.t == "READY":
            self.ready.set()

    async def _read(self) -> None:
        if not self._ws:
            raise Exception("Shard is not connected to the gateway while trying to read data")

        async for message in self._ws:  # type: ignore
            message: WSMessage

            if message.type == WSMsgType.TEXT:
                message_data = message.json()

                if s := message_data.get("s"):
                    if (not self._seq) or self._seq < s:
                        # There's a bug in the gateway where it will send a seq lower than the current one
                        # and that breaks stuff, so we only set the seq if it's higher than the current seq.

                        self._seq = s

                await self._dispatch(message_data)

        await self._handle_disconnect(self._ws.close_code or 1000)

    async def _heartbeat(self, delay: float) -> None:
        delay = delay / 1000

        await sleep(randrange(0, int(delay)))

        while True:
            if self._last_ack and time() - self._last_ack >= delay:  # type: ignore
                return await self.close()

            self._last_hb = time()

            await self.send({"op": GatewayOps.HEARTBEAT, "d": self._seq})

            await sleep(delay)
