from pathlib import Path

import pandas as pd
import pytest

from ddmc.loaders.csv import CSV
from ddmc.pipeline import Pipeline


@pytest.mark.integration
def test_processes_data(tmp_path: Path):
    filename = "test_data.csv"
    input_dir = tmp_path / "input"
    input_dir.mkdir(exist_ok=True, parents=True)
    csv_path = tmp_path / "input" / filename
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True, parents=True)
    expected_output = output_dir / filename

    with open(csv_path, "w+") as file:
        file.writelines(
            [
                '"vehicle_id","location_raw_lat","location_raw_lon","created_timestamp"\n',
                '"bern-1",46.94083234438826,7.419139400426145,"2023-03-28 09:33:54+00"\n',
                '"bern-1",46.94610305728903,7.439152037956677,"2023-03-28 09:27:12+00"\n',
                '"bern-1",46.94969573319538,7.446109875955413,"2023-03-28 09:16:16+00"\n',
                '"bern-1",46.9494144717443,7.455317604797753,"2023-03-28 09:12:02+00"\n',
            ]
        )

    loader = CSV(expected_output)
    pipe = Pipeline(
        place="Bern, CH",
        file=csv_path,
        working_dir=output_dir,
        silent=True,
        loader=loader,
    )
    pipe.run()

    assert expected_output.exists(), "pipeline output not saved"

    df = pd.read_csv(expected_output)
    assert len(df) == 1, "wrong number of entries evaluated"
