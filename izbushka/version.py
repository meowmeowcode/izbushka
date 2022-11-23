from dataclasses import (
    dataclass,
    field,
)

from .migration import Migration


@dataclass
class Version:
    name: str
    schema: list[Migration] = field(default_factory=list)
    data: list[Migration] = field(default_factory=list)
    cleanup: list[Migration] = field(default_factory=list)
