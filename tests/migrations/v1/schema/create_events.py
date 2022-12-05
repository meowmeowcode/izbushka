from izbushka import (
    Operations,
    sql,
)


def run(op: Operations) -> None:
    query = (
        sql.Query.create_table("events")
        .columns(
            sql.Column("operation", "String"),
            sql.Column("timestamp", "DateTime64(6, 'UTC') DEFAULT now('UTC')"),
        )
        .engine("MergeTree")
        .order_by("timestamp")
    )

    op.command(query)
