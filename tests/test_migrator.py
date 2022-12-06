import pytest  # type: ignore

from izbushka.base import (
    MigrationRecord,
    MigrationsLoader,
    MigrationsRepo,
    Operations,
)
from izbushka.migrator import Migrator


def test_run(migrator: Migrator, operations: Operations) -> None:
    migrator.run()
    rows = operations.query("SELECT entity, action FROM events")

    assert rows == [
        ("user", "create"),
        ("user", "delete"),
    ]


def test_double_run(migrator: Migrator, operations: Operations) -> None:
    migrator.run()

    error = None

    try:
        migrator.run()
    except Exception as e:
        error = e

    assert error is None


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


def test_progress(
    migrator: Migrator,
    migrations_loader: MigrationsLoader,
    migrations_repo: MigrationsRepo,
) -> None:
    migrations = migrations_loader.get_all()
    migrations_repo.initialize()
    migrations_repo.save(MigrationRecord.done(migrations[0]))
    migrations_repo.save(MigrationRecord.in_progress(migrations[1]))

    assert migrator.get_status()[1] == {
        "version": "v1",
        "name": "populate_events",
        "type": "data",
        "status": "in_progress",
        "progress": "50%",
    }
