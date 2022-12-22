import pytest  # type: ignore

from izbushka.entities import (
    HistoryRecord,
    MigrationInfo,
    MigrationType,
)
from izbushka.errors import OperationError
from izbushka.migrations_service import MigrationsService
from izbushka.protocols import (
    HistoryRepo,
    MigrationsRepo,
    Operations,
)


@pytest.fixture(autouse=True)
def setup(clean_db: None) -> None:
    pass


def test_run(migrations_service: MigrationsService, operations: Operations) -> None:
    migrations_service.run()
    rows = operations.query("SELECT entity, action FROM events")

    assert rows == [
        ("user", "create"),
        ("user", "delete"),
    ]


def test_double_run(
    migrations_service: MigrationsService, operations: Operations
) -> None:
    migrations_service.run()

    error = None

    try:
        migrations_service.run()
    except Exception as e:
        error = e

    assert error is None


def test_status(migrations_service: MigrationsService) -> None:
    assert migrations_service.get_status() == [
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

    migrations_service.run()

    assert migrations_service.get_status() == [
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
    migrations_service: MigrationsService, broken_migrations_repo: MigrationsRepo
) -> None:
    migrations_service.migrations_repo = broken_migrations_repo

    with pytest.raises(Exception):
        migrations_service.run()

    assert migrations_service.get_status() == [
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
    migrations_service: MigrationsService,
    migrations_repo: MigrationsRepo,
    history_repo: HistoryRepo,
) -> None:
    migrations = migrations_repo.get_all()
    history_repo.initialize()
    history_repo.save(HistoryRecord.done(migrations[0]))
    history_repo.save(HistoryRecord.in_progress(migrations[1]))

    assert migrations_service.get_status()[1] == {
        "version": "v1",
        "name": "populate_events",
        "type": "data",
        "status": "in_progress",
        "progress": "50%",
    }


def test_add_with_default_type(
    new_migrations_service: MigrationsService, new_migrations_repo: MigrationsRepo
) -> None:
    new_migrations_service.add(name="create_tables", version="v1")

    assert new_migrations_repo.get_all()[-1].info == MigrationInfo(
        name="create_tables",
        version="v1",
        type_=MigrationType.schema,
    )


def test_add_with_type(
    new_migrations_service: MigrationsService, new_migrations_repo: MigrationsRepo
) -> None:
    new_migrations_service.add(
        name="migrate_data", version="v1", type_=MigrationType.data
    )

    assert new_migrations_repo.get_all()[-1].info == MigrationInfo(
        name="migrate_data",
        version="v1",
        type_=MigrationType.data,
    )


def test_add_to_last_version(
    new_migrations_service: MigrationsService, new_migrations_repo: MigrationsRepo
) -> None:
    new_migrations_service.add(name="m1", version="v1")
    new_migrations_service.add(name="m2", version="v2")
    new_migrations_service.add(name="m3")

    assert new_migrations_repo.get_all()[-1].info == MigrationInfo(
        name="m3",
        version="v2",
        type_=MigrationType.schema,
    )


def test_add_first_without_version(
    new_migrations_service: MigrationsService, new_migrations_repo: MigrationsRepo
) -> None:
    with pytest.raises(OperationError) as err:
        new_migrations_service.add(name="create_tables")

    assert str(err.value) == "A version is required for the first migration"


def test_migration_uniqueness(
    new_migrations_service: MigrationsService, new_migrations_repo: MigrationsRepo
) -> None:
    new_migrations_service.add(name="create_tables", version="v1")

    with pytest.raises(OperationError) as err:
        new_migrations_service.add(name="create_tables")

    assert str(err.value) == "A migration with this name already exists"
