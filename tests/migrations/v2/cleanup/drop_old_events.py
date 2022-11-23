from clickhouse_connect.driver import Client  # type: ignore


def run(client: Client) -> None:
    client.command("DROP TABLE events_tmp")
