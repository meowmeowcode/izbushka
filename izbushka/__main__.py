import os

import yaml

from . import cli
from .entities import Config
from .history_repo import HistoryDBRepo
from .migrations_repo import MigrationsPackageRepo
from .migrations_service import MigrationsService
from .operations import ClickHouseConnectOperations


try:
    with open("izbushka.yml") as f:
        conf = yaml.safe_load(f)
except FileNotFoundError:
    cli.init()


config = Config(
    host=os.getenv("CLICKHOUSE_HOST") or conf.get("host") or "localhost",
    port=int(os.getenv("CLICKHOUSE_PORT") or conf.get("port") or 8123),
    username=(os.getenv("CLICKHOUSE_USERNAME") or conf.get("username") or "Default"),
    password=os.getenv("CLICKHOUSE_PASSWORD") or conf.get("password") or "",
    database=os.getenv("CLICKHOUSE_DATABASE") or conf.get("database") or "default",
    interface=os.getenv("CLICKHOUSE_INTERFACE") or conf.get("interface") or "http",
    cluster=os.getenv("CLICKHOUSE_CLUSTER") or conf.get("cluster"),
)

operations = ClickHouseConnectOperations(config)
history_repo = HistoryDBRepo(operations)
migrations_repo = MigrationsPackageRepo(conf["migrations_package"])

migrations_service = MigrationsService(
    operations=operations,
    history_repo=history_repo,
    migrations_repo=migrations_repo,
)

cmd = cli.build_cmd(migrations_service=migrations_service)
cmd()
