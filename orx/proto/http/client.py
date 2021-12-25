from typing import Protocol

from aiohttp import ClientResponse

from orx.src.http.file import File
from orx.utils import JSON, UNSET, Unset

from .ratelimiter import RatelimiterProto
from .route import RouteProto


class ClientProto(Protocol):
    def __init__(
        self,
        token: str,
        api_url: str,
        default_headers: dict[str, str] = None,
        max_retries: int = 3,
        ratelimiter: RatelimiterProto = None,
    ) -> None:
        ...

    async def request(
        self,
        route: RouteProto,
        query_params: dict[str, str | int] = None,
        headers: dict[str, str] = None,
        max_retries: int = 3,
        files: list[File] = None,
        json: JSON | Unset = UNSET,
        **kwargs,
    ) -> ClientResponse:
        ...
