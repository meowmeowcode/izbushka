.. _api:

API Reference
=============

* :class:`izbushka.Operations`
* :class:`izbushka.sql.Query`
* :class:`izbushka.sql.ClickHouseCreateQueryBuilder`
* :class:`izbushka.sql.ClickHouseExchangeQueryBuilder`

Interaction with ClickHouse
---------------------------

.. module:: izbushka

.. autoclass:: Operations
    :members:

.. module:: izbushka.sql


Building queries
----------------

.. autoclass:: Query
    :members:

.. class:: ClickHouseCreateQueryBuilder

    Builder for CREATE queries
    with additional support of ClickHouse operations.

    .. method:: on_cluster(cluster: str) -> ClickHouseCreateQueryBuilder

    Add an ON CLUSTER clause to a query.

    :param cluster: Name of the cluster.

    .. method:: engine(engine: str, *args: str) -> ClickHouseCreateQueryBuilder

    Add an ENGINE clause to a query.

    :param engine: Name of the engine.
    :param args: Engine parameters.

    .. method:: order_by(order: str) -> ClickHouseCreateQueryBuilder

    Add an ORDER BY clause to a query.

    .. method:: as_table(self, table: str) -> ClickHouseCreateQueryBuilder

    Add an AS clause to a query
    to create a table with a schema similar to another table.

    :param table: Name of a table whose schema must be used
        to create a new table.

.. class:: ClickHouseExchangeQueryBuilder

    Builder for EXCHANGE queries.

    .. method:: exchange_tables(table1: str, table2: str) -> ClickHouseExchangeQueryBuilder

    Add an EXCHANGE statement to a query.

    :param table1: First table in the statement.
    :param table2: Second table in the statement.

    .. method:: on_cluster(cluster: str) -> ClickHouseExchangeQueryBuilder:

    Add an ON CLUSTER clause to a query.

    :param cluster: Name of the cluster.
