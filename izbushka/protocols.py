from typing import (
    Any,
    Iterable,
    Protocol,
    Sequence,
    Union,
)

from .entities import (
    Config,
    HistoryRecord,
    Migration,
    NewMigration,
)
from . import sql


class HistoryRepo(Protocol):
    def initialize(self) -> None:
        ...

    def get_all(self) -> list[HistoryRecord]:
        ...

    def save(self, record: HistoryRecord) -> None:
        ...


class MigrationsRepo(Protocol):
    def get_all(self) -> list[Migration]:
        ...

    def save(self, migration: NewMigration) -> None:
        ...


class Operations(Protocol):
    config: Config

    @property
    def client(self) -> Any:
        """Client for interaction with ClickHouse.
        Use this property when methods of the ``Operations``
        class are not enough.
        """
        ...

    def command(self, query: Union[str, sql.Query]) -> Union[str, int, Sequence[str]]:
        """Query the database and get a result as a single value."""
        ...

    def query(self, query: Union[str, sql.Query]) -> Sequence[Sequence]:
        """Query the database and get a result as a sequence of rows."""
        ...

    def insert(
        self,
        table: Union[str, sql.Table],
        data: Sequence[Sequence],
        column_names: Union[str, Iterable[str]] = "*",
    ) -> None:
        """Insert a sequence of rows to a table.

        :param table: Table to insert rows into.
        :param data: Rows to insert.
        :param column_names: Column names."""
        ...
