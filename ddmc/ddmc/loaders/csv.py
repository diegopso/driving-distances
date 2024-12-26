"""Module to host classes to handle CSV data loading."""

import csv
from pathlib import Path

import pandas as pd


class CSV:
    """Allow loading data to CSV files."""

    def __init__(self, output_path: str | Path) -> None:
        self.output_path = Path(output_path)

    def load(self, df: pd.DataFrame) -> None:
        """Save the data to a CSV file.

        Parameters
        ----------
        df : DataFrame
            The dataframe to be saved to a file.

        """
        df.to_csv(self.output_path, index=False, quoting=csv.QUOTE_NONNUMERIC)
