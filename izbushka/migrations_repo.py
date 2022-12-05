from .base import (
    MigrationRecord,
    MigrationStatus,
    MigrationType,
    Operations,
)


class DBMigrationsRepo:
    table = "izbushka_migrations"

    def __init__(self, operations: Operations) -> None:
        self.operations = operations

    def initialize(self) -> None:
        self.operations.command(
            f"""
                CREATE TABLE IF NOT EXISTS {self.table} (
                    name String,
                    version String,
                    status String,
                    type String,
                    timestamp DateTime64(9, 'UTC') DEFAULT now64(9, 'UTC')
                ) ENGINE MergeTree ORDER BY timestamp
            """
        )

    def get_all(self) -> list[MigrationRecord]:
        result = self.operations.query(
            f"""
                SELECT name, version, status, type
                FROM {self.table} as t1
                JOIN (
                    SELECT MAX(timestamp) as ts
                    FROM {self.table}
                    GROUP BY name, version, type
                ) as t2
                ON t1.timestamp = t2.ts
                ORDER BY version, name, type
            """
        )

        return [
            MigrationRecord(
                name=name,
                version=version,
                status=MigrationStatus[status],
                type_=MigrationType[type_],
            )
            for name, version, status, type_ in result
        ]

    def save(self, record: MigrationRecord) -> None:
        self.operations.insert(
            self.table,
            [(record.name, record.version, record.status.name, record.type_.name)],
            column_names=("name", "version", "status", "type"),
        )
