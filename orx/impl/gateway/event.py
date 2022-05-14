from dataclasses import dataclass
from typing import Any, Optional

from discord_typings.gateway import GatewayEvent as GatewayEventType

from orx.proto.gateway import ShardProto


@dataclass(frozen=True, slots=True)
class GatewayEvent:
    shard: ShardProto
    op: int
    data: Optional[GatewayEventType] = None
    s: Optional[int] = None
    t: Optional[str] = None

    @property
    def d(self) -> Any:
        return self.data["d"]  # type: ignore

    @property
    def dispatch_name(self) -> str:
        if self.t:
            return self.t.upper()
        return f"OP_{self.op}"
