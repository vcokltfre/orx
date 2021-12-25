from typing import Protocol


class RouteProto(Protocol):
    bucket: str

    def __init__(self, method: str, path: str, **params: str | int) -> None:
        ...
