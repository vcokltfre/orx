from typing import Literal, Optional


class Route:
    def __init__(self, method: str, path: str, **params) -> None:
        guild_id: Optional[int] = params.get("guild_id")
        channel_id: Optional[int] = params.get("channel_id")
        webhook_id: Optional[int] = params.get("webhook_id")
        webhook_token: Optional[str] = params.get("webhook_token")

        self.method = method
        self.url = path.format(**params)

        webhook_bucket: Optional[str] = None
        if webhook_id:
            webhook_bucket = f"{webhook_id}:{webhook_token}"

        self.bucket = f"{path}-{guild_id}:{channel_id}:{webhook_bucket}"
