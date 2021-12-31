from __future__ import annotations

from typing import TYPE_CHECKING

from orx.proto.gateway import GatewayClientProto
from orx.proto.http import ClientProto

if TYPE_CHECKING:
    from orx.src.client import Resolver


class ConnectionState:
    def __init__(self, http: ClientProto, resolver: Resolver, gateway: GatewayClientProto = None) -> None:
        self.http = http
        self.resolver = resolver
        self.gateway = gateway

    def __str__(self) -> str:
        return f"<ConnectionState http={self.http} gateway={self.gateway}>"

    def __repr__(self) -> str:
        return str(self)
