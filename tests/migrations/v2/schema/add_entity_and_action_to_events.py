from clickhouse_connect.driver import Client  # type: ignore


def run(client: Client) -> None:
    client.command(
        """
            CREATE table events_tmp (
                entity String,
                action String,
                timestamp DateTime64(6, 'UTC') DEFAULT now('UTC')
            ) ENGINE MergeTree ORDER BY timestamp
        """
    )

    client.command("EXCHANGE TABLES events_tmp AND events")
