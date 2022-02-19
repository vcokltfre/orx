from __future__ import annotations

from typing import TYPE_CHECKING

from orx.impl.http import Route
from orx.utils import UNSET, UnsetOr

from .asset import Asset
from .object import Object, StatefulObject
from .state import ConnectionState

if TYPE_CHECKING:
    from orx.objects import DMChannel


class User(StatefulObject):
    __smart_repr__ = (
        "id",
        "username",
        "discriminator",
        "avatar",
        "bot",
        "verified",
        "banner",
    )

    def __init__(self, state: ConnectionState, data: dict) -> None:
        """A representation of a Discord user. This should not be constructed manually.

        Args:
            state (ConnectionState): The connection state.
            data (dict): The data to construct the user from.
        """

        super().__init__(data["id"], state)

        self.username: str = data["username"]
        self.discriminator: str = data["discriminator"]
        self.bot: bool = data.get("bot", False)
        self.system: bool = data.get("system", False)
        self.mfa_enabled: UnsetOr[bool] = data.get("mfa_enabled", UNSET)
        self.accent_color: int | None = data.get("accent_color", None)
        self.locale: str | None = data.get("locale", None)
        self.verified: bool = data.get("verified", False)
        self.email: str | None = data.get("email", None)
        self.flags: int = data.get("flags", 0)
        self.premium_type: int = data.get("premium_type", 0)
        self.public_flags: int = data.get("public_flags", 0)

        avatar = data["avatar"]

        self.default_avatar = Asset._from_default_avatar(self.state, int(self.discriminator) % 5)
        self.avatar = Asset._from_avatar(state, self.id, avatar) if avatar else self.default_avatar

        banner = data.get("banner", None)

        self.banner = Asset._from_user_banner(self.state, self.id, banner) if banner else None

    @classmethod
    async def me(cls, state: ConnectionState) -> "User":
        response = await state.http.request(Route("GET", "/users/@me"))
        return cls(state, await response.json())

    async def leave_guild(self, guild: Object) -> None:
        """Leave a guild.

        Args:
            guild (Object): The guild to leave.
        """

        await self.state.http.request(Route("DELETE", f"/users/@me/guilds/{guild.id}"))

    async def create_dm(self, user: Object) -> DMChannel:
        """Create a direct message channel with a user.

        Args:
            user (Object): The user to create a DM with.
        """

        response = await self.state.http.request(Route("POST", f"/users/@me/channels"), json={"recipient_id": user.id})
        data = await response.json()

        return self.state.resolver.DMChannel(self.state, data)
