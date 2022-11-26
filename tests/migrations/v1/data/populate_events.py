from clickhouse_connect.driver import Client  # type: ignore


def run(client: Client) -> None:
    rows = [
        ["user.create"],
        ["user.delete"],
    ]
    client.insert("events", rows, column_names=["operation"])


def get_progress(client: Client) -> str:
    return "50%"
