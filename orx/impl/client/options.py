from typing import Type

from orx.impl.gateway import GatewayClient
from orx.impl.http import HTTPClient
from orx.proto.gateway import GatewayClientProto, GatewayRatelimiterProto, ShardProto
from orx.proto.http import ClientProto, RatelimiterProto


class Options:
    def __init__(
        self,
        *,
        http_cls: Type[ClientProto] = None,
        gateway_cls: Type[GatewayClientProto] = None,
        api_url: str = "https://discord.com/api/v9",
        headers: dict[str, str] = None,
        http_retries: int = 3,
        http_ratelimiter: RatelimiterProto = None,
        gateway_ratelimiter: Type[GatewayRatelimiterProto] = None,
        shard_cls: Type[ShardProto] = None,
        dispatch_raw_events: bool = False,
    ) -> None:
        self.http_cls = http_cls or HTTPClient
        self.gateway_cls = gateway_cls or GatewayClient
        self.api_url = api_url
        self.headers = headers
        self.http_retries = http_retries
        self.http_ratelimiter = http_ratelimiter
        self.gateway_ratelimiter = gateway_ratelimiter
        self.shard_cls = shard_cls
        self.dispatch_raw_events = dispatch_raw_events