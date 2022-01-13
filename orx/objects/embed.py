from datetime import datetime

from orx.utils import UNSET, OptionalUnsetOr, Unset, UnsetOr, filter_unset


class EmbedField:
    def __init__(self, name: str, value: str, inline: UnsetOr[bool] = UNSET) -> None:
        self.name = name
        self.value = value
        self.inline = inline

    def json(self) -> dict:
        return filter_unset(
            {
                "name": self.name,
                "value": self.value,
                "inline": self.inline,
            }
        )


class Embed:
    def __init__(
        self,
        title: OptionalUnsetOr[str] = UNSET,
        description: OptionalUnsetOr[str] = UNSET,
        color: OptionalUnsetOr[int] = UNSET,
        timestamp: OptionalUnsetOr[datetime] = UNSET,
        url: OptionalUnsetOr[str] = UNSET,
    ) -> None:
        self.title = title
        self.description = description
        self.color = color
        self.timestamp = timestamp
        self.url = url

        self.fields = []

        self.type: str | None = None

    def add_field(self, name: str, value: str, inline: bool | Unset = UNSET) -> "Embed":
        self.fields.append(EmbedField(name, value, inline))
        return self

    def serialise(self) -> dict:
        return filter_unset(
            {
                "title": self.title,
                "description": self.description,
                "color": self.color,
                "timestamp": self.timestamp.isoformat() if self.timestamp else UNSET,
                "fields": [field.json() for field in self.fields],
            }
        )

    @classmethod
    def from_json(cls, data: dict) -> "Embed":
        embed = cls()

        embed.title = data.get("title")
        embed.description = data.get("description")
        embed.color = data.get("color")
        embed.timestamp = datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else UNSET

        embed.fields = [EmbedField(**field) for field in data.get("fields", [])]

        embed.type = data.get("type")

        return embed
