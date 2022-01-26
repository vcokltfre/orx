from datetime import datetime

from orx.utils import snowflake_time

from .repr import SmartReprMixin
from .state import ConnectionState


class Object(SmartReprMixin):
    """
    Representation of a generic Discord API object.
    """

    __smart_repr__ = ("id",)

    def __init__(self, id: int) -> None:
        self.id = id

    def __str__(self) -> str:
        return str(self.id)

    @property
    def created_at(self) -> datetime:
        """
        Returns the creation date of this object.
        """

        return snowflake_time(self.id)


class StatefulObject(Object):
    """
    Representation of a Discord API object with a connection state.
    """

    __smart_repr__ = (
        "id",
        "state",
    )

    def __init__(self, id: int, state: ConnectionState) -> None:
        super().__init__(id)
        self.state = state
