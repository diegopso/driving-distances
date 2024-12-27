import json
import os
from typing import Any, Generator

import pytest
from flask.testing import FlaskClient
from testcontainers.mysql import MySqlContainer

from api.service import create_service


@pytest.fixture()
def integration_client(database: MySqlContainer) -> Generator[FlaskClient, Any, Any]:
    os.environ["DB_HOST"] = (
        f"{database.get_container_host_ip()}:{database.get_exposed_port(port=3306)}"
    )
    os.environ["DB_DATABASE"] = database.dbname
    os.environ["DB_USERNAME"] = database.username
    os.environ["DB_PASSWORD"] = database.password

    app = create_service()
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app.test_client()


@pytest.fixture()
def client() -> Generator[FlaskClient, Any, Any]:
    app = create_service()
    app.config.update({"TESTING": True, "DEBUG": True})

    yield app.test_client()


def test_request_index(client: FlaskClient):
    response = client.get("/api")
    assert b"It Works!" in response.data


@pytest.mark.integration
def test_request_driven_distances(integration_client: FlaskClient):
    response = integration_client.get("/api/driving-distances")
    result: list = json.loads(response.data)

    assert len(result) == 1
    row = result.pop()
    assert row["vehicle_id"] == "1"
    assert row["day"] == "Tue, 31 Dec 2024 00:00:00 GMT"
    assert row["km_driven"] == 5.0
