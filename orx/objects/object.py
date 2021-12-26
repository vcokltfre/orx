from datetime import datetime

from orx.utils import snowflake_time

from .state import ConnectionState


class Object:
    """
    Representation of a generic Discord API object.
    """

    def __init__(self, id: int) -> None:
        self.id = id

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return f"<Object id={self.id}>"

    @property
    def created_at(self) -> datetime:
        """
        Returns the creation date of this object.
        """

        return snowflake_time(self.id)


class StatefulObject(Object):
    def __init__(self, id: int, state: ConnectionState) -> None:
        super().__init__(id)
        self.state = state

    def __repr__(self) -> str:
        return f"<StatefulObject id={self.id} state={self.state}>"
