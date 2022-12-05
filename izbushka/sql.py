from __future__ import annotations

from typing import (
    Any,
    Optional,
    Union,
)

from pypika import (  # type: ignore
    Column,
    Table as _Table,
)
from pypika import dialects as _dialects  # type: ignore


class Table(_Table):
    def __init__(
        self,
        name: str,
        schema=None,
        alias=None,
        query_cls=None,
    ) -> None:
        super().__init__(
            name=name,
            schema=schema,
            alias=alias,
            query_cls=query_cls,
        )

        self._cluster: Optional[str] = None

    @_dialects.builder
    def on_cluster(self, cluster: str) -> Table:  # type: ignore
        if self._cluster:
            raise AttributeError("'Query' object already has attribute cluster")
        self._cluster = cluster

    def get_sql(self, **kwargs: Any) -> str:
        sql = super().get_sql(**kwargs)
        if self._cluster:
            sql = f"{sql} ON CLUSTER {self._cluster}"
        return sql


class Query(_dialects.ClickHouseQuery):
    @classmethod
    def create_table(cls, table: Union[Table, str]) -> _ClickHouseCreateQueryBuilder:
        return _ClickHouseCreateQueryBuilder().create_table(table)

    @classmethod
    def exchange_tables(cls, table1: str, table2: str) -> Query:
        return _ClickHouseExchangeQueryBuilder().exchange_tables(table1, table2)


class _ClickHouseCreateQueryBuilder(_dialects.CreateQueryBuilder):
    QUERY_CLS = Query

    def __init__(self) -> None:
        super().__init__(dialect=_dialects.Dialects.CLICKHOUSE)
        self._engine: Optional[str] = None
        self._order_by: Optional[str] = None

    @_dialects.builder
    def engine(self, engine: str) -> _ClickHouseCreateQueryBuilder:  # type: ignore
        if self._engine:
            raise AttributeError("'CreateQuery' object already has attribute engine")
        self._engine = engine

    @_dialects.builder
    def order_by(self, order: str) -> _ClickHouseCreateQueryBuilder:  # type: ignore
        if self._order_by:
            raise AttributeError("'CreateQuery' object already has attribute engine")
        self._order_by = order

    def get_sql(self, **kwargs: Any) -> str:
        query = super().get_sql(**kwargs)

        if self._engine is not None:
            query = f"{query} ENGINE = {self._engine}"

        if self._order_by is not None:
            query = f"{query} ORDER BY {self._order_by}"

        return query


class _ClickHouseExchangeQueryBuilder:
    def __init__(self) -> None:
        self._table1: Optional[str] = None
        self._table2: Optional[str] = None
        self._cluster: Optional[str] = None

    @_dialects.builder
    def exchange_tables(self, table1: str, table2: str) -> _ClickHouseExchangeQueryBuilder:  # type: ignore
        self._table1 = table1
        self._table2 = table2

    @_dialects.builder
    def on_cluster(self, cluster: str) -> _ClickHouseExchangeQueryBuilder:  # type: ignore
        if self._cluster:
            raise AttributeError("'ExchangeQuery' object already has attribute cluster")

        self._cluster = cluster

    def get_sql(self, **kwargs: Any) -> str:
        query = f"EXCHANGE TABLES {self._table1} AND {self._table2}"

        if self._cluster is not None:
            query += f" ON CLUSTER {self._cluster}"

        return query

    def __str__(self) -> str:
        return self.get_sql()

    def __repr__(self) -> str:
        return self.__str__()
