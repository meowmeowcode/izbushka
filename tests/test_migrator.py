from clickhouse_connect.driver import Client  # type: ignore

from izbushka.migrator import Migrator


def test_run(migrator: Migrator, client: Client) -> None:
    migrator.run()
    rows = client.query("SELECT entity, action FROM events")

    assert rows.result_set == [
        ("user", "create"),
        ("user", "delete"),
    ]
