from typing import Optional, Protocol


class RouteProto(Protocol):
    bucket: str
    method: str
    url: str

    def __init__(
        self,
        method: str,
        path: str,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        webhook_id: Optional[int] = None,
        webhook_token: Optional[str] = None,
    ) -> None:
        ...
