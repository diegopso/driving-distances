"""Module to host request validation classes."""

from __future__ import annotations

from datetime import date

from pydantic import (  # tpye: ignore[import-not-found]
    BaseModel,
    Field,
    ValidationInfo,
    field_validator,
)


class GetDrivingDistancesRequest(BaseModel):
    """Validate the inputs for the get driven distances query."""

    vehicle_id: str = Field(
        default="", description="The ID of the vehicle to be queried"
    )
    start_date: date | None = Field(
        default=None, description="The start date of the query"
    )
    end_date: date | None = Field(default=None, description="The end date of the query")

    @field_validator("end_date")
    @classmethod
    def _validate_date_range(cls, end_date: date, info: ValidationInfo):
        start_date = info.data["start_date"]
        if end_date is not None and start_date is not None and end_date <= start_date:
            raise ValueError("end_date must be later than start_date")
        return end_date
