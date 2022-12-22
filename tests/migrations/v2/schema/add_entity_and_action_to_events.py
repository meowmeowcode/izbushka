from izbushka import (
    Operations,
    sql,
)


def run(op: Operations) -> None:
    if op.config.cluster:
        table, tmp_table = "events_local", "events_local_tmp"
    else:
        table, tmp_table = "events", "events_tmp"

    op.command(
        sql.Query.create_table(tmp_table)
        .if_not_exists()
        .on_cluster(op.config.cluster)
        .columns(
            sql.Column("entity", "String"),
            sql.Column("action", "String"),
            sql.Column("timestamp", "DateTime64(6, 'UTC') DEFAULT now('UTC')"),
        )
        .engine("ReplicatedMergeTree" if op.config.cluster else "MergeTree")
        .order_by("timestamp")
    )

    op.command(
        sql.Query.exchange_tables(tmp_table, table).on_cluster(op.config.cluster)
    )

    if op.config.cluster:
        op.command(sql.Query.drop_table("events").on_cluster(op.config.cluster))

        for distributed, local in (
            ("events", "events_local"),
            ("events_tmp", "events_local_tmp"),
        ):
            op.command(
                sql.Query.create_table(distributed)
                .if_not_exists()
                .on_cluster(op.config.cluster)
                .as_table(f"{op.config.database}.{local}")
                .engine(
                    "Distributed",
                    op.config.cluster,
                    op.config.database,
                    local,
                    "rand()",
                )
            )
