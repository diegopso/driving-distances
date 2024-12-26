from pathlib import Path

import pandas as pd
import pytest

from ddmc.loaders.csv import CSV


@pytest.fixture()
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({"A": [1, 2, 3], "B": [1, 2, 3]})


@pytest.fixture()
def loader(tmp_path: Path) -> CSV:
    file_path = tmp_path / "test.csv"
    return CSV(file_path)


def test_saves(tmp_path: Path, sample_df: pd.DataFrame) -> None:
    file_path = tmp_path / "test.csv"
    loader = CSV(file_path)
    loader.load(sample_df)

    assert loader.output_path.exists(), "loader didnt save file"

    df = pd.read_csv(loader.output_path)
    assert len(df) == 3, "wrong data saved"


def test_fails_to_save_in_unexistent_dir(
    tmp_path: Path, sample_df: pd.DataFrame
) -> None:
    file_path = tmp_path / "not-found" / "test.csv"
    loader = CSV(file_path)
    with pytest.raises(OSError, match="Cannot save file"):
        loader.load(sample_df)
