import datetime
from typing import Any, Generator

import pytest
from testcontainers.mysql import MySqlContainer  # type: ignore[import-untyped]

from api.repositories import DrivenDistanceRepository
from api.validator import GetDrivingDistancesRequest


@pytest.fixture()
def repository(
    database: MySqlContainer,
) -> Generator[DrivenDistanceRepository, Any, Any]:
    yield DrivenDistanceRepository(
        f"{database.get_container_host_ip()}:{database.get_exposed_port(port=3306)}",
        database.dbname,
        database.username,
        database.password,
    )


@pytest.mark.integration
def test_gets_driving_distances_from_db(repository: DrivenDistanceRepository):
    result = repository.get_driving_distances()
    assert len(result) == 1

    row = result.pop()
    assert row["vehicle_id"] == "1"
    assert row["day"] == datetime.date(2024, 12, 31)
    assert row["km_driven"] == 5.0


@pytest.mark.integration
def test_gets_driving_distances_from_db_with_date_range(
    repository: DrivenDistanceRepository,
):
    result = repository.get_driving_distances(
        GetDrivingDistancesRequest(
            start_date=datetime.date(2024, 12, 30), end_date=datetime.date(2025, 1, 1)
        )
    )
    assert len(result) == 1

    result = repository.get_driving_distances(
        GetDrivingDistancesRequest(
            start_date=datetime.date(2025, 1, 1), end_date=datetime.date(2025, 1, 2)
        )
    )
    assert len(result) == 0


@pytest.mark.integration
def test_gets_driving_distances_from_db_with_vehicle_id(
    repository: DrivenDistanceRepository,
):
    result = repository.get_driving_distances(
        GetDrivingDistancesRequest(vehicle_id="1")
    )
    assert len(result) == 1

    result = repository.get_driving_distances(
        GetDrivingDistancesRequest(vehicle_id="2")
    )
    assert len(result) == 0
