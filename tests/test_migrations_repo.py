from pathlib import Path

import pytest  # type: ignore

from izbushka.entities import (
    Migration,
    MigrationInfo,
    MigrationType,
    NewMigration,
)
from izbushka.protocols import MigrationsRepo


def test_get_all(migrations_repo: MigrationsRepo) -> None:
    from .migrations.v1.schema import create_events
    from .migrations.v1.data import populate_events
    from .migrations.v2.schema import add_entity_and_action_to_events
    from .migrations.v2.data import move_events
    from .migrations.v2.cleanup import drop_old_events

    assert migrations_repo.get_all() == [
        Migration(
            info=MigrationInfo(
                version="v1",
                type_=MigrationType.schema,
                name="create_events",
            ),
            run=create_events.run,
        ),
        Migration(
            info=MigrationInfo(
                version="v1",
                type_=MigrationType.data,
                name="populate_events",
            ),
            run=populate_events.run,
            get_progress=populate_events.get_progress,
        ),
        Migration(
            info=MigrationInfo(
                version="v2",
                type_=MigrationType.schema,
                name="add_entity_and_action_to_events",
            ),
            run=add_entity_and_action_to_events.run,
        ),
        Migration(
            info=MigrationInfo(
                version="v2",
                type_=MigrationType.data,
                name="move_events",
            ),
            run=move_events.run,
        ),
        Migration(
            info=MigrationInfo(
                version="v2",
                type_=MigrationType.cleanup,
                name="drop_old_events",
            ),
            run=drop_old_events.run,
        ),
    ]


@pytest.mark.parametrize("type_", list(MigrationType))
def test_save(type_: MigrationType, new_migrations_repo: MigrationsRepo) -> None:
    new_migration = NewMigration(
        info=MigrationInfo(
            version="v1",
            type_=type_,
            name="do_something",
        )
    )
    new_migrations_repo.save(new_migration)
    migrations = [m for m in new_migrations_repo.get_all() if m.info.type_ == type_]
    last_migration = migrations[-1]
    assert last_migration.info == new_migration.info


def test_new_migration_files(
    new_migrations_repo: MigrationsRepo, new_migrations_path: Path
) -> None:
    migrations = [
        NewMigration(
            info=MigrationInfo(
                version="v1",
                type_=MigrationType.schema,
                name="m1",
            )
        ),
        NewMigration(
            info=MigrationInfo(
                version="v1",
                type_=MigrationType.schema,
                name="m2",
            )
        ),
        NewMigration(
            info=MigrationInfo(
                version="v1",
                type_=MigrationType.data,
                name="dm1",
            )
        ),
        NewMigration(
            info=MigrationInfo(
                version="v1",
                type_=MigrationType.data,
                name="dm2",
            )
        ),
        NewMigration(
            info=MigrationInfo(
                version="v1",
                type_=MigrationType.cleanup,
                name="cl1",
            )
        ),
        NewMigration(
            info=MigrationInfo(
                version="v1",
                type_=MigrationType.cleanup,
                name="cl2",
            )
        ),
        NewMigration(
            info=MigrationInfo(
                version="v2",
                type_=MigrationType.schema,
                name="m1",
            )
        ),
        NewMigration(
            info=MigrationInfo(
                version="v2",
                type_=MigrationType.schema,
                name="m2",
            )
        ),
        NewMigration(
            info=MigrationInfo(
                version="v2",
                type_=MigrationType.data,
                name="dm1",
            )
        ),
        NewMigration(
            info=MigrationInfo(
                version="v2",
                type_=MigrationType.data,
                name="dm2",
            )
        ),
        NewMigration(
            info=MigrationInfo(
                version="v2",
                type_=MigrationType.cleanup,
                name="cl1",
            )
        ),
        NewMigration(
            info=MigrationInfo(
                version="v2",
                type_=MigrationType.cleanup,
                name="cl2",
            )
        ),
    ]

    for migration in migrations:
        new_migrations_repo.save(migration)

    expected_files = list(
        map(
            lambda p: new_migrations_path / p,
            [
                "__init__.py",
                "v1/__init__.py",
                "v1/cleanup/__init__.py",
                "v1/cleanup/cl1.py",
                "v1/cleanup/cl2.py",
                "v1/data/__init__.py",
                "v1/data/dm1.py",
                "v1/data/dm2.py",
                "v1/schema/__init__.py",
                "v1/schema/m1.py",
                "v1/schema/m2.py",
                "v2/__init__.py",
                "v2/cleanup/__init__.py",
                "v2/cleanup/cl1.py",
                "v2/cleanup/cl2.py",
                "v2/data/__init__.py",
                "v2/data/dm1.py",
                "v2/data/dm2.py",
                "v2/schema/__init__.py",
                "v2/schema/m1.py",
                "v2/schema/m2.py",
            ],
        )
    )

    actual_files = sorted(new_migrations_path.rglob("*.py"))
    assert actual_files == expected_files


def test_migrations_order(new_migrations_repo: MigrationsRepo) -> None:
    m1 = NewMigration(
        info=MigrationInfo(
            version="v1",
            type_=MigrationType.schema,
            name="do_something",
        )
    )

    m2 = NewMigration(
        info=MigrationInfo(
            version="v2",
            type_=MigrationType.schema,
            name="do_something",
        )
    )

    m3 = NewMigration(
        info=MigrationInfo(
            version="v10",
            type_=MigrationType.schema,
            name="do_something",
        )
    )

    new_migrations_repo.save(m1)
    new_migrations_repo.save(m2)
    new_migrations_repo.save(m3)

    assert [m.info for m in new_migrations_repo.get_all()] == [
        m1.info,
        m2.info,
        m3.info,
    ]
