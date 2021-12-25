from datetime import datetime, timezone

DISCORD_EPOCH = 1420070400000


def snowflake_time(id: int) -> datetime:
    """
    Returns the creation date of a snowflake.
    """

    timestamp = ((id >> 22) + DISCORD_EPOCH) / 1000
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
