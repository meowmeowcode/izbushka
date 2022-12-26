from pathlib import Path
from typing import Optional

import click
import yaml
from click import Group

from .entities import MigrationType
from .errors import OperationError
from .migrations_service import MigrationsService


@click.command
@click.argument("migrations_package")
def init(migrations_package: str) -> None:
    with click.open_file("izbushka.yml", "w") as f:
        yaml.safe_dump({"migrations_package": migrations_package}, f)

    path = Path(*migrations_package.split("."))

    if not path.exists():
        path.mkdir()
        (path / "__init__.py").touch()


def build_cmd(migrations_service: MigrationsService) -> Group:
    @click.group
    def cmd() -> None:
        pass

    @cmd.command
    def run() -> None:
        click.echo("Applying migrations...", nl=False)
        migrations_service.run()
        click.echo(" [DONE]")

    @cmd.command
    def status() -> None:
        status = migrations_service.get_status()
        click.echo(yaml.safe_dump(status))

    @cmd.command
    @click.argument("name")
    @click.option("--version", "-v")
    @click.option("--type", "-t")
    def add(name: str, version: Optional[str], type: Optional[str]) -> None:
        try:
            migrations_service.add(
                name=name,
                version=version,
                type_=None if type is None else MigrationType[type],
            )
        except OperationError as err:
            click.echo(str(err), err=True)

    return cmd
