from typing import Optional


class Route:
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
        """Represents a route to a Discord API route/path, with an HTTP verb.

        Args:
            method (str): The method of the route.
            path (str): The main route path.
            guild_id (Optional[int], optional): The guild ID to format the route path with. Defaults to None.
            channel_id (Optional[int], optional): The channel ID to format the route path with. Defaults to None.
            webhook_id (Optional[int], optional): The webhook ID to format the route path with. Defaults to None.
            webhook_token (Optional[str], optional): The webhook token to format the route path with. Defaults to None.
        """

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
