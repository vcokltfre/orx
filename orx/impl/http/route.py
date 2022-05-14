from typing import Optional


class Route:
    """
    Represents a route to a Discord API route/path, with an HTTP verb.
    """

    __slots__ = (
        "method",
        "url",
        "bucket",
    )

    def __init__(
        self,
        method: str,
        path: str,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        webhook_id: Optional[int] = None,
        webhook_token: Optional[str] = None,
    ) -> None:
        self.method = method
        self.url = path.format(
            guild_id=guild_id,
            channel_id=channel_id,
            webhook_id=webhook_id,
            webhook_token=webhook_token,
        )

        webhook_bucket: Optional[str] = None
        if webhook_id:
            webhook_bucket = f"{webhook_id}:{webhook_token}"

        self.bucket = f"{path}-{guild_id}:{channel_id}:{webhook_bucket}"
