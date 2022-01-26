from __future__ import annotations

from typing import TYPE_CHECKING

from .object import StatefulObject
from .user import User


class Member(User):
    pass


class Guild(StatefulObject):
    pass
