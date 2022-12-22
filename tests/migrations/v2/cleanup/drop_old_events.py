from izbushka import (
    Operations,
    sql,
)


def run(op: Operations) -> None:
    query = sql.Query.drop_table("events_tmp").on_cluster(op.config.cluster)
    op.command(query)

    if op.config.cluster:
        op.command(
            sql.Query.drop_table("events_local_tmp").on_cluster(op.config.cluster)
        )
