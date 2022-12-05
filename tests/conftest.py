import pytest  # type: ignore

from izbushka import (
    Config,
    Operations,
)
from izbushka.base import (
    Migration,
    MigrationsLoader,
    MigrationsRepo,
)
from izbushka.migrations_loader import PackageMigrationsLoader
from izbushka.migrations_repo import DBMigrationsRepo
from izbushka.migrator import Migrator
from izbushka.operations import ClickHouseConnectOperations


@pytest.fixture
def config() -> Config:
    return Config(
        host="localhost",
        port=8123,
        username="izbushka",
        password="izbushka",
        database="izbushka",
    )


@pytest.fixture
def operations(config: Config) -> Operations:
    return ClickHouseConnectOperations(config)


@pytest.fixture
def migrations_loader() -> MigrationsLoader:
    from . import migrations

    return PackageMigrationsLoader(migrations)


@pytest.fixture
def broken_migrations_loader() -> MigrationsLoader:
    from . import migrations

    def broken_migration(op: Operations) -> None:
        raise RuntimeError("test")

    class BrokenMigrationsLoader(PackageMigrationsLoader):
        def get_all(self) -> list[Migration]:
            result = super().get_all()
            result[2].run = broken_migration
            return result

    return BrokenMigrationsLoader(migrations)


@pytest.fixture
def migrations_repo(operations: Operations) -> MigrationsRepo:
    return DBMigrationsRepo(operations)


@pytest.fixture
def migrator(
    migrations_loader: MigrationsLoader,
    migrations_repo: MigrationsRepo,
    operations: Operations,
) -> Migrator:
    return Migrator(
        migrations_loader=migrations_loader,
        migrations_repo=migrations_repo,
        operations=operations,
    )


@pytest.fixture(autouse=True)
def clean_db(operations: Operations) -> None:
    operations.command("DROP TABLE IF EXISTS izbushka_migrations")
    operations.command("DROP TABLE IF EXISTS events")
    operations.command("DROP TABLE IF EXISTS events_tmp")
