from typing import Literal


class Unset:
    def __bool__(self) -> Literal[False]:
        return False


UNSET = Unset()

JSON = bool | int | str | list["JSON"] | dict[str, "JSON"] | None
