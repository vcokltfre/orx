from typing import Literal, TypeVar, Union


class Unset:
    def __bool__(self) -> Literal[False]:
        return False


UNSET = Unset()

T = TypeVar("T", covariant=True)

UnsetOr = Union[T, Unset]
