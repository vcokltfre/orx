# A large portion of this file is adapted from Nextcord/discord.py's Asset file:
# https://github.com/nextcord/nextcord/blob/master/nextcord/asset.py

from orx.errors import OrxError
from orx.impl.http import Route

from .state import ConnectionState

CDN_URL = "https://cdn.discordapp.com"


class Asset:
    __slots__ = (
        "_state",
        "url",
        "key",
        "animated",
    )

    def __init__(self, state: ConnectionState | None, url: str, key: str, animated: bool = False) -> None:
        self._state = state

        self.url = CDN_URL + url
        self.key = key
        self.animated = animated

    def __repr__(self):
        short = self.url.replace(CDN_URL, "")
        return f"<Asset url={short!r}>"

    async def read(self) -> bytes:
        if not self._state:
            raise OrxError("Asset is has no state and cannot be read")

        response = await self._state.http.request(Route("GET", self.url))
        return await response.read()

    @classmethod
    def _from_default_avatar(cls, state, index: int) -> "Asset":
        return cls(
            state,
            url=f"{CDN_URL}/embed/avatars/{index}.png",
            key=str(index),
            animated=False,
        )

    @classmethod
    def _from_avatar(cls, state, user_id: int, avatar: str) -> "Asset":
        animated = avatar.startswith("a_")
        format = "gif" if animated else "png"
        return cls(
            state,
            url=f"{CDN_URL}/avatars/{user_id}/{avatar}.{format}?size=1024",
            key=avatar,
            animated=animated,
        )

    @classmethod
    def _from_guild_avatar(cls, state, guild_id: int, member_id: int, avatar: str) -> "Asset":
        animated = avatar.startswith("a_")
        format = "gif" if animated else "png"
        return cls(
            state,
            url=f"{CDN_URL}/guilds/{guild_id}/users/{member_id}/avatars/{avatar}.{format}?size=1024",
            key=avatar,
            animated=animated,
        )

    @classmethod
    def _from_icon(cls, state, object_id: int, icon_hash: str, path: str) -> "Asset":
        return cls(
            state,
            url=f"{CDN_URL}/{path}-icons/{object_id}/{icon_hash}.png?size=1024",
            key=icon_hash,
            animated=False,
        )

    @classmethod
    def _from_cover_image(cls, state, object_id: int, cover_image_hash: str) -> "Asset":
        return cls(
            state,
            url=f"{CDN_URL}/app-assets/{object_id}/store/{cover_image_hash}.png?size=1024",
            key=cover_image_hash,
            animated=False,
        )

    @classmethod
    def _from_guild_image(cls, state, guild_id: int, image: str, path: str) -> "Asset":
        return cls(
            state,
            url=f"{CDN_URL}/{path}/{guild_id}/{image}.png?size=1024",
            key=image,
            animated=False,
        )

    @classmethod
    def _from_guild_icon(cls, state, guild_id: int, icon_hash: str) -> "Asset":
        animated = icon_hash.startswith("a_")
        format = "gif" if animated else "png"
        return cls(
            state,
            url=f"{CDN_URL}/icons/{guild_id}/{icon_hash}.{format}?size=1024",
            key=icon_hash,
            animated=animated,
        )

    @classmethod
    def _from_sticker_banner(cls, state, banner: int) -> "Asset":
        return cls(
            state,
            url=f"{CDN_URL}/app-assets/710982414301790216/store/{banner}.png",
            key=str(banner),
            animated=False,
        )

    @classmethod
    def _from_user_banner(cls, state, user_id: int, banner_hash: str) -> "Asset":
        animated = banner_hash.startswith("a_")
        format = "gif" if animated else "png"
        return cls(
            state,
            url=f"{CDN_URL}/banners/{user_id}/{banner_hash}.{format}?size=512",
            key=banner_hash,
            animated=animated,
        )
