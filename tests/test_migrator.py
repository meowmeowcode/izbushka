import pytest  # type: ignore
from clickhouse_connect.driver import Client  # type: ignore

from izbushka.base import MigrationsLoader
from izbushka.migrator import Migrator


def test_run(migrator: Migrator, client: Client) -> None:
    migrator.run()
    rows = client.query("SELECT entity, action FROM events")

    assert rows.result_set == [
        ("user", "create"),
        ("user", "delete"),
    ]


def test_status(migrator: Migrator) -> None:
    assert migrator.get_status() == [
        {
            "version": "v1",
            "name": "create_events",
            "type": "schema",
            "status": "pending",
        },
        {
            "version": "v1",
            "name": "populate_events",
            "type": "data",
            "status": "pending",
        },
        {
            "version": "v2",
            "name": "add_entity_and_action_to_events",
            "type": "schema",
            "status": "pending",
        },
        {"version": "v2", "name": "move_events", "type": "data", "status": "pending"},
        {
            "version": "v2",
            "name": "drop_old_events",
            "type": "cleanup",
            "status": "pending",
        },
    ]

    migrator.run()

    assert migrator.get_status() == [
        {"version": "v1", "name": "create_events", "type": "schema", "status": "done"},
        {"version": "v1", "name": "populate_events", "type": "data", "status": "done"},
        {
            "version": "v2",
            "name": "add_entity_and_action_to_events",
            "type": "schema",
            "status": "done",
        },
        {"version": "v2", "name": "move_events", "type": "data", "status": "done"},
        {
            "version": "v2",
            "name": "drop_old_events",
            "type": "cleanup",
            "status": "done",
        },
    ]


def test_status_with_failed_migration(
    migrator: Migrator, broken_migrations_loader: MigrationsLoader
) -> None:
    migrator.migrations_loader = broken_migrations_loader

    with pytest.raises(Exception):
        migrator.run()

    assert migrator.get_status() == [
        {"version": "v1", "name": "create_events", "type": "schema", "status": "done"},
        {"version": "v1", "name": "populate_events", "type": "data", "status": "done"},
        {
            "version": "v2",
            "name": "add_entity_and_action_to_events",
            "type": "schema",
            "status": "failed",
        },
        {"version": "v2", "name": "move_events", "type": "data", "status": "pending"},
        {
            "version": "v2",
            "name": "drop_old_events",
            "type": "cleanup",
            "status": "pending",
        },
    ]
