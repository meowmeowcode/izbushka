import clickhouse_connect  # type: ignore
import pytest  # type: ignore


@pytest.fixture
def client():
    return clickhouse_connect.get_client(
        host="localhost",
        port=8123,
        username="izbushka",
        password="izbushka",
        database="izbushka",
    )
