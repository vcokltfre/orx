from orx.proto.gateway import GatewayClientProto
from orx.proto.http import ClientProto


class ConnectionState:
    def __init__(self, http: ClientProto, gateway: GatewayClientProto | None = None) -> None:
        self.http = http
        self.gateway = gateway

    def __str__(self) -> str:
        return f"<ConnectionState http={self.http} gateway={self.gateway}>"

    def __repr__(self) -> str:
        return str(self)
