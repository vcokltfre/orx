from typing import TYPE_CHECKING, Any, Protocol

from aiohttp import ClientResponse, ClientWebSocketResponse

from orx.utils import JSON, UNSET, UnsetOr

from .ratelimiter import RatelimiterProto
from .route import RouteProto

if TYPE_CHECKING:
    from orx.impl.http.file import File
else:
    File = Any


class ClientProto(Protocol):
    def __init__(
        self,
        token: str = None,
        *,
        api_url: str,
        default_headers: dict[str, str] = None,
        max_retries: int = 3,
        ratelimiter: RatelimiterProto = None,
    ) -> None:
        ...

    async def ws_connect(self, url: str, **kwargs) -> ClientWebSocketResponse:
        ...

    async def request(
        self,
        route: RouteProto,
        query_params: dict[str, str | int] = None,
        headers: dict[str, str] = None,
        max_retries: int = None,
        files: UnsetOr[list[File]] = UNSET,
        json: UnsetOr[JSON] = UNSET,
        **kwargs,
    ) -> ClientResponse:
        ...
