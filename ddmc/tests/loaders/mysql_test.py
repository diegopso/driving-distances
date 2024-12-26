from typing import Any, Generator

import pandas as pd
import pytest
from testcontainers.mysql import MySqlContainer  # type: ignore[import-untyped]

from ddmc.loaders.mysql import MySQL


@pytest.fixture()
def database() -> Generator[tuple[MySqlContainer, str], Any, Any]:
    with MySqlContainer() as db:
        table_name = "test_driven_distances"
        db.exec(f"""
            CREATE TABLE {table_name} (
                `id` BIGINT NOT NULL AUTO_INCREMENT,
                `vehicle_id` VARCHAR(255) NOT NULL,
                `day` DATE NOT NULL,
                `km_driven` FLOAT NOT NULL,
                PRIMARY KEY (id)
            );
        """)

        yield db, table_name


def test_saves_to_db(database: tuple[MySqlContainer, str]) -> None:
    db, table_name = database
    loader = MySQL(
        table=table_name,
        host_name=f"{db.get_container_host_ip()}:{db.get_exposed_port(port=3306)}",
        db_name=db.dbname,
        user=db.username,
        password=db.password,
    )

    df = pd.DataFrame(
        {
            "vehicle_id": ["bern-1", "bern-2"],
            "day": ["2019-05-31", "2019-05-31"],
            "km_driven": [6.852044743674312, 5.349171694607154],
        }
    )

    loader.load(df)

    result = db.exec(f"SELECT count(id) from {table_name};")
    assert len(result) == 2, "no results saved"
