from dataclasses import dataclass
from enum import Enum, auto

from orx.proto.gateway import ShardProto
from orx.utils import JSON, UNSET, UnsetOr


class EventDirection(Enum):
    INCOMING = auto()
    OUTGOING = auto()


@dataclass(frozen=True, slots=True)
class GatewayEvent:
    shard: ShardProto
    direction: EventDirection
    raw: dict[str, JSON]
    op: int
    d: UnsetOr[JSON] = UNSET
    s: int | None = None
    t: str | None = None

    @property
    def dispatch_name(self) -> str:
        if self.t:
            return self.t.upper()
        return f"OP_{self.op}"
