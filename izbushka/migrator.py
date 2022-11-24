from clickhouse_connect.driver import Client  # type: ignore

from .base import (
    MigrationRecord,
    MigrationsLoader,
    MigrationsRepo,
)


class Migrator:
    def __init__(
        self,
        migrations_loader: MigrationsLoader,
        migrations_repo: MigrationsRepo,
        client: Client,
    ) -> None:
        self.migrations_loader = migrations_loader
        self.migrations_repo = migrations_repo
        self.client = client

    def run(self) -> None:
        self.migrations_repo.initialize()
        migrations = self.migrations_loader.get_all()

        for migration in migrations:
            self.migrations_repo.save(MigrationRecord.in_progress(migration))
            try:
                migration.run(self.client)
            except Exception as ex:
                self.migrations_repo.save(MigrationRecord.failed(migration))
                raise ex
            else:
                self.migrations_repo.save(MigrationRecord.done(migration))

    def get_status(self) -> list[dict]:
        self.migrations_repo.initialize()
        migrations = self.migrations_loader.get_all()
        migration_records = self.migrations_repo.get_all()

        records_dict = {(r.version, r.name): r for r in migration_records}

        return [
            {
                "version": m.version,
                "name": m.name,
                "type": m.type_.name,
                "status": (
                    records_dict[(m.version, m.name)].status.name
                    if (m.version, m.name) in records_dict
                    else "pending"
                ),
            }
            for m in migrations
        ]
