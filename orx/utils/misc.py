from datetime import datetime, timezone
from typing import Any

from .types import UNSET

DISCORD_EPOCH = 1420070400000


def snowflake_time(id: int) -> datetime:
    """
    Returns the creation date of a snowflake.
    """

    timestamp = ((id >> 22) + DISCORD_EPOCH) / 1000
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def filter_unset(object: Any) -> Any:
    if isinstance(object, dict):
        return {key: filter_unset(value) for key, value in object.items() if value is not UNSET}
    if isinstance(object, list):
        return [filter_unset(value) for value in object if value is not UNSET]
    return object
