import pytest  # type: ignore

from izbushka.base import (
    MigrationRecord,
    MigrationStatus,
    MigrationType,
    MigrationsRepo,
)


@pytest.fixture(autouse=True)
def setup(migrations_repo: MigrationsRepo) -> None:
    migrations_repo.initialize()


def test_status_update(migrations_repo: MigrationsRepo) -> None:
    record = MigrationRecord(
        version="v1",
        name="test",
        type_=MigrationType.schema,
        status=MigrationStatus.done,
    )

    record2 = MigrationRecord(
        version="v1",
        name="test2",
        type_=MigrationType.schema,
        status=MigrationStatus.in_progress,
    )

    migrations_repo.save(record)
    migrations_repo.save(record2)

    assert migrations_repo.get_all() == [record, record2]

    record2.status = MigrationStatus.done
    migrations_repo.save(record2)
    assert migrations_repo.get_all() == [record, record2]
