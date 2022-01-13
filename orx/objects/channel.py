from enum import IntEnum

from orx.src.http import File, Route
from orx.utils import UNSET, OptionalUnsetOr, UnsetOr, filter_unset

from .embed import Embed
from .object import Object, StatefulObject
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


class AllowedMentions:
    def __init__(
        self,
        users: UnsetOr[list[Object | int] | bool] = UNSET,
        roles: UnsetOr[list[Object | int] | bool] = UNSET,
        everyone: UnsetOr[bool] = UNSET,
        replied_user: UnsetOr[bool] = UNSET,
    ) -> None:
        self.users = users
        self.roles = roles
        self.everyone = everyone
        self.replied_user = replied_user

    def serialise(self) -> dict:
        data = {}
        parse = []

        if self.users is True:
            parse.append("users")
        elif self.users:
            data["users"] = [user.id if isinstance(user, Object) else user for user in self.users]

        if self.roles is True:
            parse.append("roles")
        elif self.roles:
            data["roles"] = [role.id if isinstance(role, Object) else role for role in self.roles]

        if self.everyone is True:
            parse.append("everyone")

        if self.replied_user is True:
            parse.append("replied_user")

        if parse:
            data["parse"] = parse

        return data


class MessageReference:
    def __init__(
        self,
        message_id: UnsetOr[int] = UNSET,
        channel_id: UnsetOr[int] = UNSET,
        guild_id: UnsetOr[int] = UNSET,
        fail_if_not_exists: UnsetOr[bool] = UNSET,
    ) -> None:
        self.message_id = message_id
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.fail_if_not_exists = fail_if_not_exists

    def serialise(self) -> dict:
        return filter_unset(
            {
                "message_id": self.message_id,
                "channel_id": self.channel_id,
                "guild_id": self.guild_id,
                "fail_if_not_exists": self.fail_if_not_exists,
            }
        )


class Messageable:
    state: ConnectionState
    id: int

    async def send(
        self,
        content: OptionalUnsetOr[str] = UNSET,
        tts: OptionalUnsetOr[bool] = UNSET,
        embeds: OptionalUnsetOr[list[Embed]] = UNSET,
        allowed_mentions: OptionalUnsetOr[AllowedMentions] = UNSET,
        files: UnsetOr[list[File]] = UNSET,
    ) -> None:
        """
        Send a message to this channel.
        """

        data = filter_unset(
            {
                "content": content,
                "tts": tts,
            }
        )

        if embeds:
            data["embeds"] = [embed.serialise() for embed in embeds]

        if allowed_mentions:
            data["allowed_mentions"] = allowed_mentions.serialise()

        response = await self.state.http.request(
            Route("POST", "/channels/{channel_id}/messages", channel_id=self.id),
            json=data,
            files=files,
        )

        return await response.json()


class DiscordChannel(StatefulObject):
    type: int

    def __init__(self, state: ConnectionState, id: int) -> None:
        super().__init__(id, state)


class DMChannel(DiscordChannel, Messageable):
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


class TextChannel(DiscordChannel, Messageable):
    def __init__(self, state: ConnectionState, data: dict) -> None:
        super().__init__(state, data["id"])

        self.name: str = data["name"]
        self.topic: str | None = data.get("topic", None)
        self.position: int = data["position"]
        self.last_message_id: int | None = data.get("last_message_id", None)
        self.nsfw: bool = data.get("nsfw", False)
        self.permission_overwrites: list[dict] | None = data.get("permission_overwrites", None)
        self.rate_limit_per_user: int | None = data.get("rate_limit_per_user", None)
        self.last_pin_timestamp: int | None = data.get("last_pin_timestamp", None)

        self.type = ChannelType.GUILD_TEXT
