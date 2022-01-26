from __future__ import annotations

from typing import TYPE_CHECKING

from .object import StatefulObject

if TYPE_CHECKING:
    from orx.objects import User


class Member(User):
    pass


class Guild(StatefulObject):
    pass
