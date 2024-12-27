from datetime import date

import pytest
from pydantic import ValidationError

from api.validator import GetDrivingDistancesRequest


def test_empty_validate_request():
    request = GetDrivingDistancesRequest()
    assert request.vehicle_id == ""
    assert request.start_date is None
    assert request.end_date is None


def test_validate_valid_request():
    request = GetDrivingDistancesRequest(
        vehicle_id="1", start_date=date(2024, 1, 1), end_date=date(2024, 1, 2)
    )
    assert request.vehicle_id == "1"
    assert request.start_date == date(2024, 1, 1)
    assert request.end_date == date(2024, 1, 2)


@pytest.mark.parametrize(
    "data,error_msg",
    [
        (
            {
                "vehicle_id": "1",
                "start_date": "01.01.2024",
                "end_date": "02.01.2024",
            },
            "Input should be a valid date",
        ),
        (
            {
                "vehicle_id": "1",
                "start_date": "2024-01-01",
                "end_date": "2024-01-01",
            },
            "end_date must be later than start_date",
        ),
    ],
)
def test_fails_validating_invalid_request(data: dict, error_msg: str):
    with pytest.raises(ValidationError, match=error_msg):
        GetDrivingDistancesRequest(**data)
