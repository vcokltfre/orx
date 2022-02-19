from dataclasses import dataclass


@dataclass(slots=True)
class VersionInfo:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


VERSION = VersionInfo(1, 0, 0)
