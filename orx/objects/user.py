from orx.src.http import Route
from orx.utils import UNSET, Unset

from .asset import Asset
from .object import StatefulObject, Object
from .state import ConnectionState


class User(StatefulObject):
    __smart_repr__ = ("id", "username", "discriminator", "avatar", "bot", "verified", "banner",)

    def __init__(self, state: ConnectionState, data: dict) -> None:
        super().__init__(data["id"], state)

        self.username: str = data["username"]
        self.discriminator: str = data["discriminator"]
        self.bot: bool = data.get("bot", False)
        self.system: bool = data.get("system", False)
        self.mfa_enabled: bool | Unset = data.get("mfa_enabled", UNSET)
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
        await self.state.http.request(Route("DELETE", f"/users/@me/guilds/{guild.id}"))

    async def create_dm(self, user: Object) -> None:
        response = await self.state.http.request(Route("POST", f"/users/@me/channels"), json={"recipient_id": user.id})

        # TODO: return the CM channel
