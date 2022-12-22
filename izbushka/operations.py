from typing import (
    Any,
    Iterable,
    Sequence,
    Union,
)

import clickhouse_connect  # type: ignore

from .entities import Config
from . import sql


class ClickHouseConnectOperations:
    def __init__(self, config: Config) -> None:
        self.config = config
        self._client: Any = None

    @property
    def client(self) -> Any:
        if self._client is None:
            self._client = clickhouse_connect.get_client(
                host=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                database=self.config.database,
                interface=self.config.interface,
            )

        return self._client

    def command(self, query: Union[str, sql.Query]) -> Union[str, int, Sequence[str]]:
        q = query if isinstance(query, str) else str(query)
        return self.client.command(q)

    def query(self, query: Union[str, sql.Query]) -> Sequence[Sequence]:
        q = query if isinstance(query, str) else str(query)
        return self.client.query(q).result_set

    def insert(
        self,
        table: Union[str, sql.Table],
        data: Sequence[Sequence],
        column_names: Union[str, Iterable[str]] = "*",
    ) -> None:
        table_name = table if isinstance(table, str) else table.get_table_name()
        self.client.insert(table_name, data, column_names=column_names)
