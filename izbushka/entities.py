from __future__ import annotations

import enum
from dataclasses import dataclass
from enum import Enum
from typing import (
    Callable,
    NamedTuple,
    Optional,
)


class MigrationType(Enum):
    schema = enum.auto()
    data = enum.auto()
    cleanup = enum.auto()


class MigrationInfo(NamedTuple):
    version: str
    name: str
    type_: MigrationType


class Status(Enum):
    pending = enum.auto()
    in_progress = enum.auto()
    failed = enum.auto()
    done = enum.auto()


@dataclass
class NewMigration:
    default_code = (
        "from izbushka import Operations\n"
        "from izbushka import sql\n"
        "\n\n"
        "def run(op: Operations) -> None:\n"
        "    ...\n"
    )

    info: MigrationInfo
    code: str = default_code


@dataclass
class Migration:
    info: MigrationInfo
    run: Callable
    get_progress: Optional[Callable] = None


@dataclass
class HistoryRecord:
    info: MigrationInfo
    status: Status

    @classmethod
    def in_progress(cls, migration: Migration) -> HistoryRecord:
        return cls(
            info=migration.info,
            status=Status.in_progress,
        )

    @classmethod
    def failed(cls, migration: Migration) -> HistoryRecord:
        return cls(
            info=migration.info,
            status=Status.failed,
        )

    @classmethod
    def done(cls, migration: Migration) -> HistoryRecord:
        return cls(
            info=migration.info,
            status=Status.done,
        )


@dataclass
class Config:
    host: str
    port: int
    username: str
    password: str
    database: str
    interface: str = "http"
    cluster: Optional[str] = None
