from typing import Literal, TypeVar, Union


class Unset:
    def __bool__(self) -> Literal[False]:
        return False


UNSET = Unset()

JSON = bool | int | str | list["JSON"] | dict[str, "JSON"] | None

T = TypeVar("T", covariant=True)

UnsetOr = Union[T, Unset]
OptionalUnsetOr = Union[T, Unset, None]
