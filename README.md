# izbushka

A database migration tool for **ClickHouse** to write migrations code in **Python** using **PyPika**.

## Documentation

The latest documentation: https://izbushka.readthedocs.io

## Migration example

```python
from izbushka import (
    Operations,
    sql,
)


def run(op: Operations) -> None:
    op.command(
        sql.Query.create_table("events")
        .if_not_exists()
        .on_cluster(op.config.cluster)
        .columns(
            sql.Column("type", "String"),
            sql.Column("timestamp", "DateTime64(6, 'UTC')"),
        )
        .engine("ReplicatedMergeTree")
        .order_by("timestamp")
    )
```
