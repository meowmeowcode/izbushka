from pathlib import Path

import pytest  # type: ignore
from clickhouse_connect.driver import Client  # type: ignore

from izbushka import (
    Migrator,
    Version,
)


@pytest.fixture(autouse=True)
def clean_db(client) -> None:
    client.command("DROP TABLE IF EXISTS events")
    client.command("DROP TABLE IF EXISTS events_tmp")


@pytest.fixture
def migrator(client: Client) -> Migrator:
    from . import migrations

    return Migrator.from_package(client, migrations)


def test_loaded_correctly(migrator: Migrator) -> None:
    from .migrations.v1.schema import create_events
    from .migrations.v1.data import populate_events
    from .migrations.v2.schema import add_entity_and_action_to_events
    from .migrations.v2.data import move_events
    from .migrations.v2.cleanup import drop_old_events

    assert migrator.versions == [
        Version(
            "v1",
            schema=[create_events],
            data=[populate_events],
        ),
        Version(
            "v2",
            schema=[add_entity_and_action_to_events],
            data=[move_events],
            cleanup=[drop_old_events],
        ),
    ]


def test_run(migrator: Migrator, client: Client) -> None:
    migrator.run()
    rows = client.query("SELECT entity, action FROM events")

    assert rows.result_set == [
        ("user", "create"),
        ("user", "delete"),
    ]
