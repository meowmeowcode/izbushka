from typing import Optional

from .entities import (
    HistoryRecord,
    MigrationInfo,
    MigrationType,
    NewMigration,
    Status,
)
from .errors import OperationError
from .protocols import (
    HistoryRepo,
    MigrationsRepo,
    Operations,
)


class MigrationsService:
    def __init__(
        self,
        migrations_repo: MigrationsRepo,
        history_repo: HistoryRepo,
        operations: Operations,
    ) -> None:
        self.migrations_repo = migrations_repo
        self.history_repo = history_repo
        self.operations = operations

    def run(self) -> None:
        self.history_repo.initialize()
        history_records = self.history_repo.get_all()
        done = {r.info for r in history_records}

        migrations = [m for m in self.migrations_repo.get_all() if m.info not in done]

        for migration in migrations:
            self.history_repo.save(HistoryRecord.in_progress(migration))
            try:
                migration.run(self.operations)
            except Exception as ex:
                self.history_repo.save(HistoryRecord.failed(migration))
                raise ex
            else:
                self.history_repo.save(HistoryRecord.done(migration))

    def get_status(self) -> list[dict]:
        self.history_repo.initialize()
        migrations = self.migrations_repo.get_all()
        history_records = self.history_repo.get_all()
        history_dict = {r.info: r for r in history_records}
        result = []

        for m in migrations:
            data = {
                "version": m.info.version,
                "name": m.info.name,
                "type": m.info.type_.name,
            }

            try:
                history_record = history_dict[m.info]
            except KeyError:
                data["status"] = "pending"
            else:
                data["status"] = history_record.status.name
                if (
                    history_record.status == Status.in_progress
                    and m.get_progress is not None
                ):
                    data["progress"] = m.get_progress(self.operations)

            result.append(data)

        return result

    def add(
        self,
        name: str,
        version: Optional[str] = None,
        type_: Optional[MigrationType] = None,
    ) -> None:
        if type_ is None:
            type_ = MigrationType.schema

        migrations = self.migrations_repo.get_all()

        if version is None:
            if not migrations:
                raise OperationError("A version is required for the first migration")

            version = migrations[-1].info.version

        if any(
            (m.info.name, m.info.version, m.info.type_) == (name, version, type_)
            for m in migrations
        ):
            raise OperationError("A migration with this name already exists")

        migration = NewMigration(
            info=MigrationInfo(
                name=name,
                version=version,
                type_=type_,
            )
        )

        self.migrations_repo.save(migration)
