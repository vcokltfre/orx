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
from .src.client import Cog, Options, OrxClient
from .version import VERSION

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
    "Cog",
    "OrxClient",
    "Options",
)

__version__ = VERSION
__author__ = "vcokltfre"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2021 vcokltfre"
