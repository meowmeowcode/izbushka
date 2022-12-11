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
