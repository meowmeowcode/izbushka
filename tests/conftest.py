import clickhouse_connect  # type: ignore
import pytest  # type: ignore
from clickhouse_connect.driver import Client  # type: ignore

from izbushka.base import (
    Migration,
    MigrationsLoader,
    MigrationsRepo,
)
from izbushka.migrations_loader import PackageMigrationsLoader
from izbushka.migrations_repo import DBMigrationsRepo
from izbushka.migrator import Migrator


@pytest.fixture
def client():
    return clickhouse_connect.get_client(
        host="localhost",
        port=8123,
        username="izbushka",
        password="izbushka",
        database="izbushka",
    )


@pytest.fixture
def migrations_loader() -> MigrationsLoader:
    from . import migrations

    return PackageMigrationsLoader(migrations)


@pytest.fixture
def broken_migrations_loader() -> MigrationsLoader:
    from . import migrations

    def broken_migration(client: Client) -> None:
        raise RuntimeError("test")

    class BrokenMigrationsLoader(PackageMigrationsLoader):
        def get_all(self) -> list[Migration]:
            result = super().get_all()
            result[2].run = broken_migration
            return result

    return BrokenMigrationsLoader(migrations)


@pytest.fixture
def migrations_repo(client: Client) -> MigrationsRepo:
    return DBMigrationsRepo(client)


@pytest.fixture
def migrator(
    migrations_loader: MigrationsLoader,
    migrations_repo: MigrationsRepo,
    client: Client,
) -> Migrator:
    return Migrator(
        migrations_loader=migrations_loader,
        migrations_repo=migrations_repo,
        client=client,
    )


@pytest.fixture(autouse=True)
def clean_db(client) -> None:
    client.command("DROP TABLE IF EXISTS izbushka_migrations")
    client.command("DROP TABLE IF EXISTS events")
    client.command("DROP TABLE IF EXISTS events_tmp")
