from clickhouse_connect.driver import Client  # type: ignore

from izbushka import sql


def run(client: Client) -> None:
    query = sql.Query.drop_table("events_tmp")
    client.command(str(query))
