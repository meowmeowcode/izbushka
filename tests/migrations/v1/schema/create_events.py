from clickhouse_connect.driver import Client  # type: ignore

from izbushka import sql


def run(client: Client) -> None:
    query = (
        sql.Query.create_table("events")
        .columns(
            sql.Column("operation", "String"),
            sql.Column("timestamp", "DateTime64(6, 'UTC') DEFAULT now('UTC')"),
        )
        .engine("MergeTree")
        .order_by("timestamp")
    )

    client.command(str(query))
