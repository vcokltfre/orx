from .errors import (
    BadGateway,
    BadRequest,
    Forbidden,
    GatewayCriticalError,
    GatewayReconnect,
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
from .src.client import OrxClient, Options

__all__ = (
    "BadGateway",
    "BadRequest",
    "Forbidden",
    "GatewayCriticalError",
    "GatewayReconnect",
    "GatewayTimeout",
    "HTTPError",
    "MethodNotAllowed",
    "NotFound",
    "OrxError",
    "ServerError",
    "ServiceUnavailable",
    "TooManyRequests",
    "Unauthorized",
    "UnprocessableEntity",
    "OrxClient",
    "Options",
)

__version__ = "1.0.0"
__author__ = "vcokltfre"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2021 vcokltfre"
