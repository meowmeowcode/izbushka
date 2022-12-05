from izbushka import (
    Operations,
    sql,
)


def run(op: Operations) -> None:
    query = sql.Query.from_("events_tmp").select("operation", "timestamp")
    result = op.query(query)
    new_rows = [row[0].split(".") for row in result]
    op.insert("events", new_rows, column_names=["entity", "action"])
