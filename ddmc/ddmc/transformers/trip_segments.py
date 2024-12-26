"""Module to handle data containing OSM node ids and timestamps to identify trip segments."""

import pandas as pd


class TripSegments:
    """Allow obtaining trip segments made by vehicles in the data."""

    def identify(self, df: pd.DataFrame) -> pd.DataFrame:
        """Combine lines of the dataframe to identify trips from the same car that took place on the same day.

        Expected columns in input dataframe: "vehicle_id", "nodes", "created_timestamp".

        Parameters
        ----------
        df : DataFrame
            The data frame carrying the data.

        Returns
        -------
        DataFrame
            The resulting data frame.

        """
        df.sort_values(
            by=["vehicle_id", "created_timestamp"], ascending=True, inplace=True
        )
        df.reset_index(inplace=True)

        dest_df = df.drop(0)
        dest_df.reset_index(inplace=True)

        df = df.add_prefix("src_")
        dest_df = dest_df.add_prefix("dest_")

        df = pd.concat([df, dest_df], axis=1, join="inner")
        df.drop(["src_index", "dest_index", "dest_level_0"], inplace=True, axis=1)

        df = df[df["src_vehicle_id"] == df["dest_vehicle_id"]]
        df.drop("dest_vehicle_id", axis=1, inplace=True)

        df = df[df["src_created_timestamp"] == df["dest_created_timestamp"]]
        df.drop("dest_created_timestamp", axis=1, inplace=True)

        df.rename(
            columns={
                "src_created_timestamp": "day",
                "src_vehicle_id": "vehicle_id",
                "src_nodes": "src_node",
                "dest_nodes": "dest_node",
                "src_location_raw_lat": "src_lat",
                "src_location_raw_lon": "src_lon",
                "dest_location_raw_lat": "dest_lat",
                "dest_location_raw_lon": "dest_lon",
            },
            inplace=True,
        )

        return df
