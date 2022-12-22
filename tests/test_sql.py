from izbushka import sql


def test_create_on_cluster() -> None:
    query = (
        sql.Query.create_table("t1").on_cluster("c1").columns(sql.Column("n", "Int64"))
    )

    assert str(query) == 'CREATE TABLE "t1" ON CLUSTER c1 ("n" Int64)'

    query = (
        sql.Query.create_table("t1").on_cluster(None).columns(sql.Column("n", "Int64"))
    )

    assert str(query) == 'CREATE TABLE "t1" ("n" Int64)'


def test_engine() -> None:
    query = (
        sql.Query.create_table("t1")
        .columns(sql.Column("n", "Int64"))
        .engine("MergeTree")
    )

    assert str(query) == 'CREATE TABLE "t1" ("n" Int64) ENGINE = MergeTree'


def test_engine_params() -> None:
    query = (
        sql.Query.create_table("t1")
        .columns(sql.Column("n", "Int64"))
        .engine("Distributed", "test_cluster", "test_database", "test_table")
    )

    assert str(query) == (
        'CREATE TABLE "t1" ("n" Int64) '
        "ENGINE = Distributed(test_cluster, test_database, test_table)"
    )


def test_order_by() -> None:
    query = sql.Query.create_table("t1").columns(sql.Column("n", "Int64")).order_by("n")
    assert str(query) == 'CREATE TABLE "t1" ("n" Int64) ORDER BY n'


def test_exchange_tables() -> None:
    query = sql.Query.exchange_tables("t1", "t2")
    assert str(query) == "EXCHANGE TABLES t1 AND t2"


def test_exchange_tables_on_cluster() -> None:
    query = sql.Query.exchange_tables("t1", "t2").on_cluster("c1")
    assert str(query) == "EXCHANGE TABLES t1 AND t2 ON CLUSTER c1"
    query = sql.Query.exchange_tables("t1", "t2").on_cluster(None)
    assert str(query) == "EXCHANGE TABLES t1 AND t2"
