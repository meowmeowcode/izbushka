from __future__ import annotations

from typing import (
    Any,
    Optional,
    Sequence,
    Union,
)

from pypika import (  # type: ignore
    Column,
    Table,
    dialects as _dialects,
)

__all__ = ("Column", "Query", "Table")


class Query(_dialects.ClickHouseQuery):
    @classmethod
    def create_table(cls, table: Union[Table, str]) -> ClickHouseCreateQueryBuilder:
        """Entry point for the builder of a CREATE query.
        Takes a name of a table to create."""
        return ClickHouseCreateQueryBuilder().create_table(table)

    @classmethod
    def exchange_tables(cls, table1: str, table2: str) -> Query:
        """Entry point for the builder of an EXCHANGE query.
        Takes names of tables to exchange."""
        return ClickHouseExchangeQueryBuilder().exchange_tables(table1, table2)


class ClickHouseCreateQueryBuilder(_dialects.CreateQueryBuilder):
    QUERY_CLS = Query

    def __init__(self) -> None:
        super().__init__(dialect=_dialects.Dialects.CLICKHOUSE)
        self._cluster: Optional[str] = None
        self._engine: Optional[str] = None
        self._engine_params: Sequence[str] = ()
        self._order_by: Optional[str] = None
        self._as_table: Optional[str] = None

    @_dialects.builder
    def on_cluster(self, cluster: str) -> ClickHouseCreateQueryBuilder:  # type: ignore
        if self._cluster:
            raise AttributeError("'CreateQuery' object already has attribute cluster")
        self._cluster = cluster

    @_dialects.builder
    def engine(  # type: ignore
        self, engine: str, *args: str
    ) -> ClickHouseCreateQueryBuilder:
        if self._engine:
            raise AttributeError("'CreateQuery' object already has attribute engine")
        self._engine = engine
        self._engine_params = args

    @_dialects.builder
    def order_by(self, order: str) -> ClickHouseCreateQueryBuilder:  # type: ignore
        if self._order_by:
            raise AttributeError("'CreateQuery' object already has attribute order_by")
        self._order_by = order

    @_dialects.builder
    def as_table(self, table: str) -> ClickHouseCreateQueryBuilder:  # type: ignore
        if self._as_table:
            raise AttributeError("'CreateQuery' object already has attribute as_table")
        self._as_table = table

    def get_sql(self, **kwargs: Any) -> str:
        self._set_kwargs_defaults(kwargs)

        if not self._create_table:
            return ""

        if not any((self._columns, self._as_select, self._as_table)):
            return ""

        create_table = self._create_table_sql(**kwargs)

        if self._as_table:
            query = f"{create_table} AS {self._as_table}"
        elif self._as_select:
            query = create_table + self._as_select_sql(**kwargs)
        else:
            body = self._body_sql(**kwargs)
            table_options = self._table_options_sql(**kwargs)

            query = "{create_table} ({body}){table_options}".format(
                create_table=create_table, body=body, table_options=table_options
            )

        if self._engine is not None:
            query = f"{query} ENGINE = {self._engine}"
            if self._engine_params:
                query = f"{query}({', '.join(self._engine_params)})"

        if self._order_by is not None:
            query = f"{query} ORDER BY {self._order_by}"

        return query

    def _create_table_sql(self, **kwargs: Any) -> str:
        query = super()._create_table_sql(**kwargs)
        if self._cluster:
            query = f"{query} ON CLUSTER {self._cluster}"
        return query


class ClickHouseExchangeQueryBuilder:
    def __init__(self) -> None:
        self._table1: Optional[str] = None
        self._table2: Optional[str] = None
        self._cluster: Optional[str] = None

    @_dialects.builder
    def exchange_tables(  # type: ignore
        self,
        table1: str,
        table2: str,
    ) -> ClickHouseExchangeQueryBuilder:
        self._table1 = table1
        self._table2 = table2

    @_dialects.builder
    def on_cluster(  # type: ignore
        self, cluster: str
    ) -> ClickHouseExchangeQueryBuilder:
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
