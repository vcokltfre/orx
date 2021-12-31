from enum import IntEnum

from .object import StatefulObject
from .state import ConnectionState


class ChannelType(IntEnum):
    """
    Enum of channel types.
    """

    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6
    GUILD_NEWS_THREAD = 10
    GUILD_PUBLIC_THREAD = 11
    GUILD_PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13


class Channel(StatefulObject):
    type: int

    def __init__(self, state: ConnectionState, id: int) -> None:
        super().__init__(id, state)


class DMChannel(Channel):
    type = ChannelType.DM

    __smart_repr__ = (
        "id",
        "last_message_id",
        "recipient",
    )

    def __init__(self, state: ConnectionState, data: dict) -> None:
        super().__init__(state, data["id"])

        self.last_message_id: int | None = data.get("last_message_id", None)
        self.recipient = state.resolver.user(state, data["recipients"][0])
