from izbushka.base import (
    Migration,
    MigrationType,
    MigrationsLoader,
)


def test_get_all(migrations_loader: MigrationsLoader) -> None:
    from .migrations.v1.schema import create_events
    from .migrations.v1.data import populate_events
    from .migrations.v2.schema import add_entity_and_action_to_events
    from .migrations.v2.data import move_events
    from .migrations.v2.cleanup import drop_old_events

    assert migrations_loader.get_all() == [
        Migration(
            version="v1",
            name="create_events",
            run=create_events.run,
            type_=MigrationType.schema,
        ),
        Migration(
            version="v1",
            name="populate_events",
            type_=MigrationType.data,
            run=populate_events.run,
            get_progress=populate_events.get_progress,
        ),
        Migration(
            version="v2",
            name="add_entity_and_action_to_events",
            type_=MigrationType.schema,
            run=add_entity_and_action_to_events.run,
        ),
        Migration(
            version="v2",
            name="move_events",
            type_=MigrationType.data,
            run=move_events.run,
        ),
        Migration(
            version="v2",
            name="drop_old_events",
            type_=MigrationType.cleanup,
            run=drop_old_events.run,
        ),
    ]
