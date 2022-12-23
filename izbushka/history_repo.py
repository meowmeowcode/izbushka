from pypika import functions as fn  # type: ignore

from . import sql
from .entities import (
    HistoryRecord,
    MigrationInfo,
    MigrationType,
    Status,
)
from .protocols import Operations


class HistoryDBRepo:
    table = sql.Table("izbushka_history")
    local_table = sql.Table("izbushka_history_local")

    def __init__(self, operations: Operations) -> None:
        self.operations = operations

    def initialize(self) -> None:
        cluster = self.operations.config.cluster

        self.operations.command(
            sql.Query.create_table(self.local_table if cluster else self.table)
            .if_not_exists()
            .on_cluster(cluster)
            .columns(
                sql.Column("name", "String"),
                sql.Column("version", "String"),
                sql.Column("type", "String"),
                sql.Column("status", "String"),
                sql.Column("timestamp", "DateTime64(9, 'UTC') DEFAULT now64(9, 'UTC')"),
            )
            .engine("ReplicatedMergeTree" if cluster else "MergeTree")
            .order_by("timestamp")
        )

        if cluster:
            self.operations.command(
                sql.Query.create_table(self.table)
                .if_not_exists()
                .on_cluster(cluster)
                .as_table(
                    f"{self.operations.config.database}."
                    f"{self.local_table.get_table_name()}"
                )
                .engine(
                    "Distributed",
                    cluster,
                    self.operations.config.database,
                    self.local_table.get_table_name(),
                    "rand()",
                )
            )

    def get_all(self) -> list[HistoryRecord]:
        t1 = self.table.as_("t1")
        t2 = self.table.as_("t2")

        max_timestamp_q = (
            sql.Query.from_(t2)
            .select(fn.Max(t2.timestamp).as_("ts"))
            .groupby("name", "version", "type")
        )

        query = (
            sql.Query.from_(t1)
            .select("version", "name", "type", "status")
            .join(max_timestamp_q)
            .on(t1.timestamp == max_timestamp_q.ts)
            .orderby("version", "name", "type")
        )

        result = self.operations.query(query)

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
