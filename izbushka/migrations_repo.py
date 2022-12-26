import importlib
from pathlib import Path
import pkgutil

from natsort import natsorted

from .entities import (
    Migration,
    MigrationInfo,
    MigrationType,
    NewMigration,
)


class MigrationsPackageRepo:
    def __init__(self, package: str) -> None:
        self.package = pkgutil.resolve_name(package)
        self.path = Path(*self.package.__path__)

    def get_all(self) -> list[Migration]:
        result = []

        version_packages = [
            p.name
            for p in pkgutil.iter_modules(
                self.package.__path__, f"{self.package.__name__}."
            )
        ]

        for v in version_packages:
            for type_ in MigrationType:
                migrations = self._load_migrations(v, type_)
                result.extend(migrations)

        return natsorted(
            result, lambda m: (m.info.version, m.info.type_.value, m.info.name)
        )

    @staticmethod
    def _load_migrations(version_path: str, type_: MigrationType) -> list[Migration]:
        version = version_path.split(".")[-1]
        path = f"{version_path}.{type_.name}"

        try:
            package = pkgutil.resolve_name(path)
        except AttributeError:
            return []

        modules = [
            importlib.import_module(m.name)
            for m in pkgutil.iter_modules(package.__path__, f"{path}.")
        ]

        return [
            Migration(
                info=MigrationInfo(
                    version=version,
                    type_=type_,
                    name=m.__name__.split(".")[-1],
                ),
                run=m.run,
                get_progress=getattr(m, "get_progress", None),
            )
            for m in modules
            if hasattr(m, "run")
        ]

    def save(self, migration: NewMigration) -> None:
        version_dir = self.path / migration.info.version

        if not version_dir.exists():
            version_dir.mkdir()
            (version_dir / "__init__.py").touch()

        type_dir = version_dir / migration.info.type_.name

        if not type_dir.exists():
            type_dir.mkdir()
            (type_dir / "__init__.py").touch()

        migration_path = type_dir / f"{migration.info.name}.py"
        migration_path.write_text(migration.code)
