from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType
from typing import Sequence

from clickhouse_connect.driver import Client  # type: ignore

from .version import Version
from .migration import Migration


class Migrator:
    def __init__(self, client: Client, versions: Sequence[Version]) -> None:
        self._client = client
        self.versions = versions

    def run(self) -> None:
        for version in self.versions:
            for step in (version.schema, version.data, version.cleanup):
                for migration in step:
                    migration.run(self._client)

    @classmethod
    def from_package(cls, client: Client, package: ModuleType) -> Migrator:
        version_packages = [
            p.name
            for p in pkgutil.iter_modules(package.__path__, f"{package.__name__}.")
        ]

        versions = [
            Version(
                name=v.split(".")[-1],
                schema=cls._load_migrations(f"{v}.schema"),
                data=cls._load_migrations(f"{v}.data"),
                cleanup=cls._load_migrations(f"{v}.cleanup"),
            )
            for v in version_packages
        ]

        return Migrator(client, versions)

    @staticmethod
    def _load_migrations(path: str) -> list[Migration]:
        try:
            package = pkgutil.resolve_name(path)
        except AttributeError:
            return []

        modules = [
            importlib.import_module(m.name)
            for m in pkgutil.iter_modules(package.__path__, f"{path}.")
        ]

        return [m for m in modules if hasattr(m, "run")]

    def get_status(self) -> dict:
        return {}
