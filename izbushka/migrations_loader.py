import importlib
import pkgutil
from types import ModuleType

from .base import (
    Migration,
    MigrationType,
)


class PackageMigrationsLoader:
    def __init__(self, package: ModuleType) -> None:
        self.package = package

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

        return result

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
                name=m.__name__.split(".")[-1],
                version=version,
                type_=type_,
                run=m.run,
                get_progress=getattr(m, "get_progress", None),
            )
            for m in modules
            if hasattr(m, "run")
        ]
