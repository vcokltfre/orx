from asyncio import sleep
from collections import defaultdict
from dataclasses import dataclass
from json import dumps
from typing import Any, Final, Mapping, Optional, Type

from aiohttp import ClientResponse, ClientSession, ClientWebSocketResponse, FormData

from orx.impl.errors import (
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
from orx.impl.types import UNSET, UnsetOr
from orx.proto.http import RatelimiterProto, RouteProto

from .file import File
from .ratelimiter import Ratelimiter

API_URL: Final[str] = "https://discord.com/api/v10"
MAX_RETRIES: Final[int] = 3


@dataclass(slots=True)
class _RequestData:
    data: Optional[FormData]
    json: UnsetOr[Any]


class HTTPClient:
    __slots__ = (
        "_token",
        "_api_url",
        "_default_headers",
        "_max_retries",
        "_ratelimiter",
        "__session",
    )

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
        token: Optional[str] = None,
        *,
        api_url: Optional[str] = None,
        default_headers: Optional[dict[str, str]] = None,
        max_retries: Optional[int] = None,
        ratelimiter: Optional[RatelimiterProto] = None,
    ) -> None:
        """The default HTTP client implementation for Orx.

        Args:
            token (Optional[str], optional): Your bot token. Defaults to None.
            api_url (Optional[str], optional): The base URL to use for requests. Defaults to "https://discord.com/api/v10".
            default_headers (Optional[dict[str, str]], optional): The default headers to send on requests. Defaults to {}.
            max_retries (Optional[int], optional): The maximum number of retries per request. Defaults to 3.
            ratelimiter (Optional[RatelimiterProto], optional): The ratelimiter class to use for request. Defaults to orx.http.Ratelimiter.
        """

        self._token = token
        self._api_url = api_url or API_URL
        self._default_headers = default_headers or {}
        self._max_retries = max_retries or 3
        self._ratelimiter = ratelimiter or Ratelimiter()

        self.__session: Optional[ClientSession] = None

    async def __aenter__(self) -> "HTTPClient":
        return self

    async def __aexit__(self, exc_type: Type[BaseException], exc_val: BaseException, exc_tb: BaseException) -> None:
        await self.close()

    @property
    def _session(self) -> ClientSession:
        if self.__session is None or self.__session.closed:
            self.__session = ClientSession(headers=self._default_headers)

        return self.__session

    @staticmethod
    def _prepare_data(attempt: int, files: UnsetOr[list[File]] = UNSET, json: UnsetOr[Any] = UNSET) -> _RequestData:
        if not files:
            return _RequestData(None, json)

        data = FormData()

        for i, file in enumerate(files):
            file.reset(attempt)

            data.add_field(f"file_{i}", file.fp, filename=file.filename)

        if json is not UNSET:
            data.add_field("payload_json", dumps(json), content_type="application/json")

        return _RequestData(data, UNSET)

    async def close(self) -> None:
        """Close the HTTP client."""

        if self.__session and not self.__session.closed:
            await self.__session.close()

    async def spawn_websocket(self, url: str, **kwargs: Any) -> ClientWebSocketResponse:
        """Spawn a WebSocket connection.

        Args:
            url (str): The URL to connect to.

        Returns:
            ClientWebSocketResponse: The open WebSocket connection.
        """

        return await self._session.ws_connect(url, **kwargs)  # type: ignore

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
        """Make a request to the Discord API.

        Args:
            route (RouteProto): The route to request.
            query_params (Optional[dict[str, str  |  int]], optional): Query parameters to send with the request. Defaults to {}.
            headers (Optional[dict[str, str]], optional): Headers to send with the request. Defaults to {}.
            max_retries (Optional[int], optional): The maximum number of retries for this request. Defaults to the HTTP client default.
            files (UnsetOr[list[File]], optional): Files to send with the request. Defaults to UNSET.
            json (UnsetOr[Any], optional): JSON data to send with the request. Defaults to UNSET.
            reason (Optional[str], optional): An audit log reason for this request. Defaults to None.

        Raises:
            TooManyRequests: A ratelimit was hit that could not be handled (Cloudflare limited).
            HTTPError: Another 4XX HTTP error was raised.
            OrxError: After all retries the server still errored.

        Returns:
            ClientResponse: The response from the API.
        """

        query_params = query_params or {}
        headers = headers or {}
        max_retries = max_retries or self._max_retries

        if self._token:
            headers["Authorization"] = f"Bot {self._token}"

        if reason:
            headers["X-Audit-Log-Reason"] = reason

        for attempt in range(max_retries or 1):
            await sleep(attempt**2 * 0.5)

            data = self._prepare_data(attempt, files, json)

            kwargs: dict[str, Any] = {}

            if data.data:
                kwargs["data"] = data.data
            elif data.json is not UNSET:
                kwargs["json"] = data.json

            async with await self._ratelimiter.acquire(route.bucket) as bucket:
                response = await self._session.request(
                    route.method,
                    f"{self._api_url}{route.url}",
                    params=query_params,
                    headers=headers,
                    **kwargs,
                )

                rl_reset_after = float(response.headers.get("X-RateLimit-Reset-After", 0))
                rl_bucket_remaining = int(response.headers.get("X-RateLimit-Remaining", 1))

                if 200 <= response.status < 300:
                    if rl_bucket_remaining == 0:
                        await bucket.defer(rl_reset_after)
                    return response

                if response.status == 429:
                    if "Via" not in response.headers:
                        # When a request goes through Discord's servers, and thus Google's
                        # load balancers, those load balancers add a `Via` header to the response.
                        # If we are ratelimited by Cloudflare then this header won't have been
                        # added by GCP, so we raise.

                        raise TooManyRequests(response)

                    response_json: dict[str, Any] = await response.json()

                    is_global = response_json.get("global", False)
                    retry_after = response_json["retry_after"]

                    if is_global:
                        await self._ratelimiter.set_global_lock(retry_after)
                    else:
                        await bucket.defer(retry_after)
                elif response.status < 500:
                    raise self._status_codes[response.status](response)

        raise OrxError(f"Failed to make request on route {route.method} {route.url} after {max_retries} attempts.")
