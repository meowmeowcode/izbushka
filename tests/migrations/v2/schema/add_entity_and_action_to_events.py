from izbushka import (
    Operations,
    sql,
)


def run(op: Operations) -> None:
    query = (
        sql.Query.create_table("events_tmp")
        .columns(
            sql.Column("entity", "String"),
            sql.Column("action", "String"),
            sql.Column("timestamp", "DateTime64(6, 'UTC') DEFAULT now('UTC')"),
        )
        .engine("MergeTree")
        .order_by("timestamp")
    )

    op.command(query)
    op.command(sql.Query.exchange_tables("events_tmp", "events"))
