"""Module to allow extracting data from CSV files."""

from pathlib import Path

import pandas as pd

_DEFAULT_TIMEZONE = "Europe/Berlin"


class _CSVColumns:
    CREATED_TIMESTAMP: str = "created_timestamp"
    VEHICLE_ID: str = "vehicle_id"
    LOCATION_RAW_LAT: str = "location_raw_lat"
    LOCATION_RAW_LON: str = "location_raw_lon"


class CSV:
    """Class to extracting data from CSV files."""

    def extract(self, file: Path | str) -> pd.DataFrame:
        """Load a CSV file into a dataframe.

        This method also parses the column `created_timestamp` into Datetime and adjusts the timezone.

        Parameters
        ----------
        file : str | Path
            The file to be loaded.

        Returns
        -------
        DataFrame
            The loaded data frame.

        """
        df = pd.read_csv(
            file,
            parse_dates=[_CSVColumns.CREATED_TIMESTAMP],
            dtype={
                _CSVColumns.VEHICLE_ID: str,
                _CSVColumns.LOCATION_RAW_LAT: float,
                _CSVColumns.LOCATION_RAW_LON: float,
            },
        )

        df[_CSVColumns.CREATED_TIMESTAMP] = df[
            _CSVColumns.CREATED_TIMESTAMP
        ].dt.tz_convert(tz=_DEFAULT_TIMEZONE)
        df[_CSVColumns.CREATED_TIMESTAMP] = df[_CSVColumns.CREATED_TIMESTAMP].dt.date

        return df
