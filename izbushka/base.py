from __future__ import annotations

import enum
from dataclasses import dataclass
from enum import Enum
from typing import (
    Any,
    Callable,
    Iterable,
    Optional,
    Protocol,
    Sequence,
    Union,
)

from . import sql


class OperationError(Exception):
    pass


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
    get_progress: Optional[Callable] = None


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


@dataclass
class Config:
    host: str
    port: int
    username: str
    password: str
    database: str
    interface: str = "http"
    cluster: Optional[str] = None


class Operations(Protocol):
    config: Config

    @property
    def client(self) -> Any:
        ...

    def command(self, query: Union[str, sql.Query]) -> Union[str, int, Sequence[str]]:
        ...

    def query(self, query: Union[str, sql.Query]) -> Sequence[Sequence]:
        ...

    def insert(
        self,
        table: Union[str, sql.Table],
        data: Sequence[Sequence],
        column_names: Union[str, Iterable[str]] = "*",
    ) -> None:
        ...


class MigrationsGenerator(Protocol):
    def initialize(self) -> None:
        ...

    def new_version(self, name: str) -> None:
        ...

    def new_migration(
        self, name: str, type_: MigrationType = MigrationType.schema
    ) -> None:
        ...
