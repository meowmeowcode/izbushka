import pytest  # type: ignore

from izbushka.entities import (
    HistoryRecord,
    Status,
    MigrationInfo,
    MigrationType,
)
from izbushka.protocols import HistoryRepo


@pytest.fixture(autouse=True)
def setup(clean_db: None, history_repo: HistoryRepo) -> None:
    history_repo.initialize()


def test_status_update(history_repo: HistoryRepo) -> None:
    record = HistoryRecord(
        info=MigrationInfo(
            version="v1",
            type_=MigrationType.schema,
            name="test",
        ),
        status=Status.done,
    )

    record2 = HistoryRecord(
        info=MigrationInfo(
            version="v1",
            type_=MigrationType.schema,
            name="test2",
        ),
        status=Status.in_progress,
    )

    history_repo.save(record)
    history_repo.save(record2)

    assert history_repo.get_all() == [record, record2]

    record2.status = Status.done
    history_repo.save(record2)
    assert history_repo.get_all() == [record, record2]
