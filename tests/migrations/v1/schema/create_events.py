from izbushka import (
    Operations,
    sql,
)


def run(op: Operations) -> None:
    table_name = "events_local" if op.config.cluster else "events"

    op.command(
        sql.Query.create_table(table_name)
        .if_not_exists()
        .on_cluster(op.config.cluster)
        .columns(
            sql.Column("operation", "String"),
            sql.Column("timestamp", "DateTime64(6, 'UTC') DEFAULT now('UTC')"),
        )
        .engine("ReplicatedMergeTree" if op.config.cluster else "MergeTree")
        .order_by("timestamp")
    )

    if op.config.cluster:
        op.command(
            sql.Query.create_table("events")
            .if_not_exists()
            .on_cluster(op.config.cluster)
            .as_table(f"{op.config.database}.events_local")
            .engine(
                "Distributed",
                op.config.cluster,
                op.config.database,
                "events_local",
                "rand()",
            )
        )
