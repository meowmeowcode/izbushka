from clickhouse_connect.driver import Client  # type: ignore

from izbushka import sql


def run(client: Client) -> None:
    query = sql.Query.from_("events_tmp").select("operation", "timestamp")
    result = client.query(str(query))
    new_rows = [row[0].split(".") for row in result.result_set]
    client.insert("events", new_rows, column_names=["entity", "action"])
