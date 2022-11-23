from clickhouse_connect.driver import Client  # type: ignore


def run(client: Client) -> None:
    client.command(
        """
            CREATE TABLE events (
                operation String,
                timestamp DateTime64(6, 'UTC') DEFAULT now('UTC')
            ) ENGINE MergeTree ORDER BY timestamp
        """
    )
