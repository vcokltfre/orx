from asyncio import sleep
from collections import defaultdict
from json import dumps  # TODO: replace with util
from typing import Mapping, Type

from aiohttp import ClientResponse, ClientSession, FormData
from loguru import logger

from orx import __version__ as VERSION
from orx.errors import (
    BadGateway,
    BadRequest,
    Forbidden,
    GatewayTimeout,
    HTTPError,
    MethodNotAllowed,
    NotFound,
    OrxError,
    ServerError,
    ServiceUnavailable,
    TooManyRequests,
    Unauthorized,
    UnprocessableEntity,
)
from orx.proto.http import RatelimiterProto, RouteProto
from orx.utils import JSON, UNSET, Unset

from .file import File
from .ratelimiter import Ratelimiter


class HTTPClient:
    _status_codes: Mapping[int, Type[HTTPError]] = defaultdict(
        lambda: HTTPError,
        {
            400: BadRequest,
            401: Unauthorized,
            403: Forbidden,
            404: NotFound,
            405: MethodNotAllowed,
            422: UnprocessableEntity,
            429: TooManyRequests,
            500: ServerError,
            502: BadGateway,
            503: ServiceUnavailable,
            504: GatewayTimeout,
        },
    )

    def __init__(
        self,
        token: str,
        api_url: str,
        default_headers: dict[str, str] = None,
        max_retries: int = 3,
        ratelimiter: RatelimiterProto = None,
    ) -> None:
        self.token = token
        self.api_url = api_url
        self.default_headers = default_headers or {}
        self.max_retries = max_retries
        self.ratelimiter = ratelimiter or Ratelimiter()

        self.default_headers["Authorization"] = f"Bot {self.token}"
        self.default_headers["User-Agent"] = f"DiscordBot (Orx {VERSION}), https://github.com/vcokltfre/Orx)"

        self.__session: ClientSession | None = None

    @property
    def _session(self) -> ClientSession:
        if self.__session is None or self.__session.closed:
            self.__session = ClientSession(headers=self.default_headers)

        return self.__session

    async def request(
        self,
        route: RouteProto,
        query_params: dict[str, str | int] = None,
        headers: dict[str, str] = None,
        max_retries: int = None,
        files: list[File] = None,
        json: JSON | Unset = UNSET,
        **kwargs,
    ) -> ClientResponse:
        headers = headers or {}
        max_retries = max_retries or self.max_retries

        if reason := kwargs.pop("reason", None):
            headers["X-Audit-Log-Reason"] = reason

        for attempt in range(max_retries or 1):
            await sleep(attempt ** 2 * 0.5)

            logger.debug(
                f"[Attempt {attempt} of {max_retries}] Making request on route {route.method} {route.url}" + f": {json}"
                if json is not UNSET
                else ""
            )

            if files:
                data = FormData()

                for i, file in enumerate(files):
                    file.reset(attempt)

                    data.add_field(f"file_{i}", file.fp, filename=file.filename)

                if json is not Unset:
                    data.add_field("payload_json", dumps(json), content_type="application/json")

                kwargs["data"] = data
            elif json is not Unset:
                kwargs["json"] = json

            bucket = await self.ratelimiter.acquire(route.bucket)

            async with bucket:
                logger.debug(f"Acquired a lock on bucket {route.bucket}")
                response = await self._session.request(
                    route.method, self.api_url + route.url, params=query_params, headers=headers, **kwargs
                )

                rl_reset_after = float(response.headers.get("X-RateLimit-Reset-After", 0))
                rl_bucket_remaining = int(response.headers.get("X-RateLimit-Remaining", 1))

                if 200 <= response.status < 300:
                    if rl_bucket_remaining == 0:
                        await bucket.defer(rl_reset_after)
                    return response

                if response.status == 429:
                    if not response.headers.get("Via"):
                        # When a request goes through Discord's servers, and thus Google's
                        # load balancers, those load balancers add a `Via` header to the response.
                        # If we are ratelimited by Cloudflare then this header won't have been
                        # added by GCP, so we raise.

                        raise TooManyRequests(response)

                    response_json: dict = await response.json()

                    is_global = response_json.get("global", False)
                    retry_after = response_json["retry_after"]

                    if is_global:
                        await self.ratelimiter.set_global_lock(retry_after)
                    else:
                        await bucket.defer(retry_after)
                else:
                    try:
                        detail = str(await response.json())
                    except Exception:
                        detail = await response.text()
                    logger.error(
                        f"Error while making request on route {route.method} {route.url}: [{response.status}] {detail}"
                    )
                    raise self._status_codes[response.status](response)

        raise OrxError(f"Failed to make request on route {route.method} {route.url} after {max_retries} attempts")
