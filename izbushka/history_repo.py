from .entities import (
    HistoryRecord,
    MigrationInfo,
    MigrationType,
    Status,
)
from .protocols import Operations


class HistoryDBRepo:
    table = "izbushka_history"

    def __init__(self, operations: Operations) -> None:
        self.operations = operations

    def initialize(self) -> None:
        self.operations.command(
            f"""
                CREATE TABLE IF NOT EXISTS {self.table} (
                    version String,
                    name String,
                    type String,
                    status String,
                    timestamp DateTime64(9, 'UTC') DEFAULT now64(9, 'UTC')
                ) ENGINE MergeTree ORDER BY timestamp
            """
        )

    def get_all(self) -> list[HistoryRecord]:
        result = self.operations.query(
            f"""
                SELECT version, name, type, status
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
            HistoryRecord(
                info=MigrationInfo(
                    version=version,
                    type_=MigrationType[type_],
                    name=name,
                ),
                status=Status[status],
            )
            for version, name, type_, status in result
        ]

    def save(self, record: HistoryRecord) -> None:
        self.operations.insert(
            self.table,
            [
                (
                    record.info.version,
                    record.info.name,
                    record.info.type_.name,
                    record.status.name,
                )
            ],
            column_names=("version", "name", "type", "status"),
        )
