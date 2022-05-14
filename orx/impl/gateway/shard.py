from asyncio import Event, Task, create_task, sleep
from random import randrange
from time import time
from typing import Any, Callable, Coroutine, Optional, Type, cast

from aiohttp import ClientWebSocketResponse, WSMsgType
from discord_typings.gateway import GatewayEvent as GatewayEventType
from discord_typings.gateway import (
    HeartbeatCommand,
    HelloEvent,
    IdentifyCommand,
    IdentifyConnectionProperties,
    IdentifyData,
    ResumeCommand,
    ResumeData,
)

from orx.impl.errors import GatewayCriticalError, GatewayReconnect
from orx.proto.gateway import Command, GatewayRatelimiterProto
from orx.proto.http import HTTPClientProto

from .enums import GatewayCloseCodes, GatewayOps
from .event import GatewayEvent

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
    __slots__ = (
        "callbacks",
        "id",
        "latency",
        "ready",
        "_count",
        "_http",
        "_token",
        "_intents",
        "_ratelimiter",
        "_session",
        "_sequence",
        "_socket",
        "_pacemaker",
        "_last_hb",
        "_last_ack",
        "_closing",
    )

    def __init__(
        self,
        id: int,
        shard_count: int,
        token: str,
        intents: int,
        ratelimiter_cls: Type[GatewayRatelimiterProto],
    ) -> None:
        self.id = id
        self.callbacks: dict[str, list[Callable[..., Coroutine[Any, Any, None]]]] = {}

        self.ready = Event()
        self.ready.clear()

        self._count = shard_count
        self._token = token
        self._intents = intents

        self._ratelimiter = ratelimiter_cls(120, 60)

        self._session: Optional[str] = None
        self._sequence: Optional[int] = None

        self._socket: Optional[ClientWebSocketResponse] = None

        self._pacemaker: Optional[Task[None]] = None
        self._last_hb: Optional[float] = None
        self._last_ack: Optional[float] = None

        self._closing: bool = False

        self.latency: Optional[float] = None

    def __repr__(self) -> str:
        return f"<Shard id={self.id} seq={self._sequence}>"

    async def _resume(self) -> None:
        if not (self._session and self._sequence):
            raise RuntimeError("Cannot resume shard with no session or sequence.")

        await self.send(
            ResumeCommand(
                op=GatewayOps.RESUME,  # type: ignore
                d=ResumeData(
                    token=self._token,
                    session_id=self._session,
                    seq=self._sequence,
                ),
            )
        )

    async def _identify(self) -> None:
        await self.send(
            IdentifyCommand(
                op=GatewayOps.IDENTIFY,  # type: ignore
                d=IdentifyData(
                    token=self._token,
                    intents=self._intents,
                    shard=[self.id, self._count],
                    properties=IdentifyConnectionProperties(
                        **{
                            "$os": "linux",
                            "$browser": "orx",
                            "$device": "orx",
                        }
                    ),
                ),  # type: ignore
            )
        )

    def _task_error(self, task: Task[None]) -> None:
        exc = task.exception()

        if not exc:
            return

        raise exc

    def _callback(self, event: GatewayEvent) -> None:
        for callback in self.callbacks.get(event.dispatch_name, []):
            task = create_task(callback(event))
            task.add_done_callback(self._task_error)

        for callback in self.callbacks.get("*", []):
            task = create_task(callback(event))
            task.add_done_callback(self._task_error)

    async def _dispatch(self, data: GatewayEventType) -> None:
        event = GatewayEvent(self, data["op"], data, data.get("s"), data.get("t"))

        try:
            self._callback(event)
        except Exception as e:
            print(f"Error in callback: {e}")

        if event.op == GatewayOps.HELLO:
            data = cast(HelloEvent, event.data)
            self._pacemaker = create_task(self._heartbeat(data["d"]["heartbeat_interval"]))
            self._pacemaker.add_done_callback(self._task_error)
            await self._identify()
        elif event.op == GatewayOps.ACK:
            self._last_ack = time()
        elif event.op == GatewayOps.RECONNECT:
            await self.close()
            raise GatewayReconnect()
        elif event.t == "READY":
            self.ready.set()

    async def _handle_disconnect(self, code: int) -> None:
        if code in CRITICAL:
            raise GatewayCriticalError(code)

        if code in NONCRITICAL:
            self._session = None
            self._sequence = None

        await self.close()

        raise GatewayReconnect()

    async def _heartbeat(self, delay: float) -> None:
        await sleep(randrange(0, int(delay)))

        while not self._closing:
            if self._last_ack and time() - self._last_ack >= delay:
                return await self.close()

            await self.send(HeartbeatCommand(op=1, d=self._sequence))
            self._last_hb = time()

            await sleep(delay)

    async def _read(self) -> None:
        if not self._socket or self._socket.closed:
            raise RuntimeError("Shard is not connected")

        async for message in self._socket:
            if message.type == WSMsgType.TEXT:  # type: ignore
                data: GatewayEventType = message.json()

                if sequence := data.get("s"):
                    if (not self._sequence) or self._sequence < sequence:
                        self._sequence = sequence

                await self._dispatch(data)

        await self._handle_disconnect(self._socket.close_code or 1000)

    async def connect(self, url: str, http: HTTPClientProto) -> None:
        if self._socket and not self._socket.closed:
            raise RuntimeError("Shard is already connected")

        self._socket = await http.spawn_websocket(url + "?v=10")

        if self._session:
            await self._resume()

        try:
            await self._read()
        except GatewayReconnect:
            pass

        if self._closing:
            return

    async def close(self) -> None:
        self._closing = True

        if self._socket and not self._socket.closed:
            await self._socket.close()

        if self._pacemaker and not self._pacemaker.cancelled():
            self._pacemaker.cancel()

    async def send(self, data: Command) -> None:
        if not self._socket or self._socket.closed:
            raise RuntimeError("Shard is not connected")

        await self._ratelimiter.acquire()

        try:
            await self._socket.send_json(data)
        except OSError:
            await self.close()
        except Exception:
            await self.close()
            raise
