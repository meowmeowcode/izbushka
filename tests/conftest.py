import shutil
from pathlib import Path
from typing import (
    Any,
    Generator,
)

import pytest  # type: ignore

from izbushka import (
    Config,
    Operations,
    sql,
)
from izbushka.entities import Migration
from izbushka.migrations_repo import MigrationsPackageRepo
from izbushka.history_repo import HistoryDBRepo
from izbushka.migrations_service import MigrationsService
from izbushka.operations import ClickHouseConnectOperations
from izbushka.protocols import (
    HistoryRepo,
    MigrationsRepo,
)


@pytest.fixture(params=(None, "test_shard_localhost"))
def config(request: Any) -> Config:
    return Config(
        host="localhost",
        port=8123,
        username="izbushka",
        password="izbushka",
        database="izbushka",
        cluster=request.param,
    )


@pytest.fixture
def operations(config: Config) -> Operations:
    return ClickHouseConnectOperations(config)


@pytest.fixture
def migrations_path() -> str:
    return "tests.migrations"


@pytest.fixture
def migrations_repo(migrations_path: str) -> MigrationsRepo:
    return MigrationsPackageRepo(migrations_path)


@pytest.fixture
def broken_migrations_repo(migrations_path: str) -> MigrationsRepo:
    def broken_migration(op: Operations) -> None:
        raise RuntimeError("test")

    class BrokenMigrationsRepo(MigrationsPackageRepo):
        def get_all(self) -> list[Migration]:
            result = super().get_all()
            result[2].run = broken_migration
            return result

    return BrokenMigrationsRepo(migrations_path)


@pytest.fixture
def new_migrations_package() -> str:
    return "tests.new_migrations"


@pytest.fixture
def new_migrations_path(new_migrations_package: str) -> Generator[Path, None, None]:
    path = Path(*new_migrations_package.split("."))

    if path.exists():
        shutil.rmtree(path)

    path.mkdir()
    (path / "__init__.py").touch()
    yield path
    shutil.rmtree(path)


@pytest.fixture
def new_migrations_repo(
    new_migrations_package: str, new_migrations_path: Path
) -> MigrationsRepo:
    return MigrationsPackageRepo(new_migrations_package)


@pytest.fixture
def history_repo(operations: Operations) -> HistoryRepo:
    return HistoryDBRepo(operations)


@pytest.fixture
def migrations_service(
    migrations_repo: MigrationsRepo,
    history_repo: HistoryRepo,
    operations: Operations,
) -> MigrationsService:
    return MigrationsService(
        migrations_repo=migrations_repo,
        history_repo=history_repo,
        operations=operations,
    )


@pytest.fixture
def new_migrations_service(
    new_migrations_repo: MigrationsRepo,
    history_repo: HistoryRepo,
    operations: Operations,
) -> MigrationsService:
    return MigrationsService(
        migrations_repo=new_migrations_repo,
        history_repo=history_repo,
        operations=operations,
    )


@pytest.fixture
def clean_db(operations: Operations, config: Config) -> None:
    operations.command(
        sql.Query.drop_table("izbushka_history").if_exists().on_cluster(config.cluster)
    )
    operations.command(
        sql.Query.drop_table("izbushka_history_local")
        .if_exists()
        .on_cluster(config.cluster)
    )
    operations.command(
        sql.Query.drop_table("events").if_exists().on_cluster(config.cluster)
    )
    operations.command(
        sql.Query.drop_table("events_local").if_exists().on_cluster(config.cluster)
    )
    operations.command(
        sql.Query.drop_table("events_tmp").if_exists().on_cluster(config.cluster)
    )
    operations.command(
        sql.Query.drop_table("events_local_tmp").if_exists().on_cluster(config.cluster)
    )
