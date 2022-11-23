from clickhouse_connect.driver import Client  # type: ignore


def run(client: Client) -> None:
    result = client.query("SELECT operation, timestamp FROM events_tmp")

    new_rows = [row[0].split(".") for row in result.result_set]

    client.insert("events", new_rows, column_names=["entity", "action"])
