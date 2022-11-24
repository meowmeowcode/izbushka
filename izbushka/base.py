from __future__ import annotations

import enum
from dataclasses import dataclass
from enum import Enum
from typing import (
    Callable,
    Protocol,
)


class MigrationStatus(Enum):
    pending = enum.auto()
    in_progress = enum.auto()
    failed = enum.auto()
    done = enum.auto()


class MigrationType(Enum):
    schema = enum.auto()
    data = enum.auto()
    cleanup = enum.auto()


@dataclass
class Migration:
    version: str
    name: str
    type_: MigrationType
    run: Callable
    # get_progress: Optional[Callable]


@dataclass
class MigrationRecord:
    version: str
    name: str
    type_: MigrationType
    status: MigrationStatus

    @classmethod
    def in_progress(cls, migration: Migration) -> MigrationRecord:
        return cls(
            version=migration.version,
            name=migration.name,
            type_=migration.type_,
            status=MigrationStatus.in_progress,
        )

    @classmethod
    def failed(cls, migration: Migration) -> MigrationRecord:
        return cls(
            version=migration.version,
            name=migration.name,
            type_=migration.type_,
            status=MigrationStatus.failed,
        )

    @classmethod
    def done(cls, migration: Migration) -> MigrationRecord:
        return cls(
            version=migration.version,
            name=migration.name,
            type_=migration.type_,
            status=MigrationStatus.done,
        )


class MigrationsLoader(Protocol):
    def get_all(self) -> list[Migration]:
        ...


class MigrationsRepo(Protocol):
    def initialize(self) -> None:
        ...

    def get_all(self) -> list[MigrationRecord]:
        ...

    def save(self, record: MigrationRecord) -> None:
        ...
