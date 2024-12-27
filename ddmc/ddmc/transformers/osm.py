"""Module to operate over lat/long and OSM map data."""

import networkx as nx  # type: ignore[import-untyped]
import osmnx as ox
import pandas as pd


class OSM:
    """Allows data transformation."""

    def __init__(self, G: nx.MultiDiGraph) -> None:
        self.G = G

    def coordinates_to_nodes(
        self,
        df: pd.DataFrame,
        lat_col: str = "location_raw_lat",
        lon_col: str = "location_raw_lon",
    ) -> pd.DataFrame:
        """Convert a series of lat and lon coordinates in a data frame to nodes in the OSM graph.

        Parameters
        ----------
        df : DataFrame
            The data frame carrying the data.
        lat_col : str
            The column name for the latitude coordinates.
        lon_col : str
            The column name for the longitude coordinates.

        Returns
        -------
        DataFrame
            The resulting data frame.

        """
        if self.G is None:
            raise RuntimeError("Load graph before using OSM class methods.")

        nodes = ox.nearest_nodes(self.G, X=df[lon_col], Y=df[lat_col])
        df["nodes"] = nodes
        return df

    def geo_distances(self, df: pd.DataFrame) -> pd.DataFrame:
        """Evaluate the geo distance between all pairs of 2 nodes in the data frame.

        Parameters
        ----------
        df : DataFrame
            The data frame carrying the data.

        Returns
        -------
        DataFrame
            The resulting data frame.

        """
        distances = ox.distance.great_circle(
            df["src_lat"].to_numpy(),
            df["src_lon"].to_numpy(),
            df["dest_lat"].to_numpy(),
            df["dest_lon"].to_numpy(),
        )

        if isinstance(distances, float):
            return distances / 1000

        df = pd.concat([df, pd.DataFrame({"km_driven": distances})], axis=1)
        df["km_driven"] = df["km_driven"].divide(1000)
        return df

    def driving_distances(
        self, df: pd.DataFrame, src_col: str = "src_node", dest_col: str = "dest_node"
    ) -> pd.DataFrame:
        """Evaluate the driving distance between 2 nodes in the OSM graph.

        Parameters
        ----------
        df : DataFrame
            The data frame carrying the data.
        src_col : str
            The column name for the source nodes.
        dest_col : str
            The column name for the destination nodes.

        Returns
        -------
        DataFrame
            The resulting data frame.

        """
        if self.G is None:
            raise Exception("Load graph before using OSM class methods.")

        df["km_driven"] = df.apply(
            lambda r: nx.shortest_path_length(
                self.G, r[src_col], r[dest_col], weight="length"
            ),
            axis=1,
        )
        df["km_driven"] = df["km_driven"].divide(1000)

        return df
