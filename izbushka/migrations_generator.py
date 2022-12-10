from pathlib import Path

from .base import (
    MigrationType,
    OperationError,
)


class PackageMigrationsGenerator:
    migration_code = (
        "from izbushka import Operations\n"
        "from izbushka import sql\n"
        "\n\n"
        "def run(op: Operations) -> None:"
        "    ...\n\n"
    )

    def __init__(self, path: str) -> None:
        self.module_path = path
        self.path = Path(*path.split("."))

    def initialize(self) -> None:
        self.path.mkdir(parents=True, exist_ok=True)
        (self.path / "__init__.py").touch()
        # create config

    def new_version(self, name: str) -> None:
        directory = self.path / name

        if directory.exists():
            raise OperationError("A version with this name already exists")

        directory.mkdir()
        (directory / "__init__.py").touch()

    def new_migration(
        self, name: str, type_: MigrationType = MigrationType.schema
    ) -> None:
        last_version = sorted(self.path.iterdir())[-1]
        type_dir = last_version / type_.name

        if not type_dir.exists():
            type_dir.mkdir()
            (type_dir / "__init__.py").touch()

        migration = type_dir / f"{name}.py"

        if migration.exists():
            raise OperationError("A migration with this name already exists")

        migration.write_text(self.migration_code)
