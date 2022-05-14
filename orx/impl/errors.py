from aiohttp import ClientResponse


class OrxError(Exception):
    """
    Base class for all Orx errors.
    """

    pass


class HTTPError(OrxError):
    """
    Base class for all HTTP errors.
    """

    def __init__(self, response: ClientResponse, *args: object) -> None:
        self.response = response
        self.status = response.status

        super().__init__(*args)


class BadRequest(HTTPError):
    pass


class Unauthorized(BadRequest):
    pass


class Forbidden(BadRequest):
    pass


class NotFound(BadRequest):
    pass


class MethodNotAllowed(BadRequest):
    pass


class UnprocessableEntity(BadRequest):
    pass


class TooManyRequests(BadRequest):
    pass


class ServerError(HTTPError):
    pass


class BadGateway(ServerError):
    pass


class ServiceUnavailable(ServerError):
    pass


class GatewayTimeout(ServerError):
    pass


class GatewayReconnect(OrxError):
    """
    Raised when a shard needs to reconnect to the gateway.
    """

    pass


class GatewayCriticalError(OrxError):
    """
    Raised when a shard encounters a critical error.
    """

    def __init__(self, code: int) -> None:
        self.code = code

        super().__init__(f"Gateway disconnected with close code {code}")
