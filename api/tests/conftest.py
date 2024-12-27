from typing import Any, Generator

import pytest
import sqlalchemy
from testcontainers.mysql import MySqlContainer  # type: ignore[import-untyped]


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run integration tests",
    )


def pytest_configure(config: pytest.Config):
    config.addinivalue_line("markers", "integration: mark test as integration to run")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]):
    if config.getoption("--integration") or len(items) == 1:
        return  # dont skip if integration flag or speciffic test selected

    skip_integration = pytest.mark.skip(reason="need --integration option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)


@pytest.fixture()
def database() -> Generator[MySqlContainer, Any, Any]:
    with MySqlContainer() as db:
        table_name = "driven_distances"

        engine = sqlalchemy.create_engine(db.get_connection_url())
        with engine.begin() as connection:
            connection.execute(
                sqlalchemy.text(f"""
                    CREATE TABLE {table_name} (
                        `id` BIGINT NOT NULL AUTO_INCREMENT,
                        `vehicle_id` VARCHAR(255) NOT NULL,
                        `day` DATE NOT NULL,
                        `km_driven` FLOAT NOT NULL,
                        PRIMARY KEY (id)
                    );
                """)
            )
            connection.execute(
                sqlalchemy.text(
                    f"INSERT INTO {table_name} (vehicle_id, day, km_driven) VALUES (1, '2024-12-31', 5)"
                )
            )

        yield db
