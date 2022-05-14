from typing import TYPE_CHECKING, Any, Optional, Protocol

from aiohttp import ClientResponse, ClientWebSocketResponse

from orx.impl.types import UNSET, UnsetOr

from .ratelimiter import RatelimiterProto
from .route import RouteProto

if TYPE_CHECKING:
    from orx.impl.http.file import File
else:
    File = Any


class HTTPClientProto(Protocol):
    def __init__(
        self,
        token: Optional[str] = None,
        *,
        api_url: Optional[str] = None,
        default_headers: Optional[dict[str, str]] = None,
        max_retries: Optional[int] = None,
        ratelimiter: Optional[RatelimiterProto] = None,
    ) -> None:
        ...

    async def spawn_websocket(self, url: str, **kwargs: Any) -> ClientWebSocketResponse:
        ...

    async def request(
        self,
        route: RouteProto,
        query_params: Optional[dict[str, str | int]] = None,
        headers: Optional[dict[str, str]] = None,
        *,
        max_retries: Optional[int] = None,
        files: UnsetOr[list[File]] = UNSET,
        json: UnsetOr[Any] = UNSET,
        reason: Optional[str] = None,
    ) -> ClientResponse:
        ...
