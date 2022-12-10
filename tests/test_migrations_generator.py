import shutil
from pathlib import Path
from typing import Any

import pytest  # type: ignore

from izbushka.base import (
    MigrationsGenerator,
    MigrationType,
    OperationError,
)
from izbushka.migrations_generator import PackageMigrationsGenerator


@pytest.fixture
def migrations_path() -> Path:
    return Path(__file__).parent / "app/migrations"


@pytest.fixture(autouse=True)
def setup(migrations_path: Path) -> Any:
    if migrations_path.exists():
        shutil.rmtree(migrations_path)

    yield

    if migrations_path.exists():
        shutil.rmtree(migrations_path)


@pytest.fixture
def migrations_generator() -> MigrationsGenerator:
    migrations_generator = PackageMigrationsGenerator("tests.app.migrations")
    migrations_generator.initialize()
    return migrations_generator


def test_generate_many_migrations(
    migrations_generator: MigrationsGenerator, migrations_path: Path
) -> None:
    migrations_generator.new_version("v1")
    migrations_generator.new_migration("m1")
    migrations_generator.new_migration("m2")
    migrations_generator.new_migration("dm1", type_=MigrationType.data)
    migrations_generator.new_migration("dm2", type_=MigrationType.data)
    migrations_generator.new_migration("cl1", type_=MigrationType.cleanup)
    migrations_generator.new_migration("cl2", type_=MigrationType.cleanup)
    migrations_generator.new_version("v2")
    migrations_generator.new_migration("m21")
    migrations_generator.new_migration("m22")
    migrations_generator.new_migration("dm21", type_=MigrationType.data)
    migrations_generator.new_migration("dm22", type_=MigrationType.data)
    migrations_generator.new_migration("cl21", type_=MigrationType.cleanup)
    migrations_generator.new_migration("cl22", type_=MigrationType.cleanup)

    expected_files = list(
        map(
            lambda p: migrations_path / p,
            [
                "__init__.py",
                "v1/__init__.py",
                "v1/cleanup/__init__.py",
                "v1/cleanup/cl1.py",
                "v1/cleanup/cl2.py",
                "v1/data/__init__.py",
                "v1/data/dm1.py",
                "v1/data/dm2.py",
                "v1/schema/__init__.py",
                "v1/schema/m1.py",
                "v1/schema/m2.py",
                "v2/__init__.py",
                "v2/cleanup/__init__.py",
                "v2/cleanup/cl21.py",
                "v2/cleanup/cl22.py",
                "v2/data/__init__.py",
                "v2/data/dm21.py",
                "v2/data/dm22.py",
                "v2/schema/__init__.py",
                "v2/schema/m21.py",
                "v2/schema/m22.py",
            ],
        )
    )

    actual_files = sorted(migrations_path.rglob("*.py"))
    assert actual_files == expected_files


def test_version_uniqueness(migrations_generator: MigrationsGenerator) -> None:
    migrations_generator.new_version("v1")

    with pytest.raises(OperationError) as err:
        migrations_generator.new_version("v1")

    assert str(err.value) == "A version with this name already exists"


def test_migration_uniqueness(migrations_generator: MigrationsGenerator) -> None:
    migrations_generator.new_version("v1")
    migrations_generator.new_migration("m")

    with pytest.raises(OperationError) as err:
        migrations_generator.new_migration("m")

    assert str(err.value) == "A migration with this name already exists"
