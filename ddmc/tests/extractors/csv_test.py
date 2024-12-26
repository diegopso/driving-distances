from pathlib import Path

import pytest

from ddmc.extractors.csv import CSV


@pytest.fixture()
def sample_csv_path(tmp_path: Path) -> Path:
    csv_path = tmp_path / "test_data.csv"

    with csv_path.open("w+") as file:
        file.writelines(
            [
                '"vehicle_id","location_raw_lat","location_raw_lon","created_timestamp"\n',
                '"bern-1",46.94083234438826,7.419139400426145,"2023-03-28 09:33:54+00"\n',
                '"bern-1",46.94610305728903,7.439152037956677,"2023-03-28 09:27:12+00"\n',
                '"bern-1",46.94969573319538,7.446109875955413,"2023-03-28 09:16:16+00"\n',
                '"bern-1",46.9494144717443,7.455317604797753,"2023-03-28 09:12:02+00"\n',
            ]
        )

    return csv_path


def test_loads_data(sample_csv_path: Path) -> None:
    df = CSV().extract(sample_csv_path)

    assert df["location_raw_lat"].dtype == "float64", "lat column not imported as float"
    assert df["location_raw_lon"].dtype == "float64", "lon column not imported as float"
    assert len(df) == 4, "wrong number of lines imported"
