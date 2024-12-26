"""Module to handle loading OSM data and converting into grphs."""

import hashlib
from pathlib import Path

import networkx as nx  # type: ignore [import-untyped]
import osmnx as ox


class OSM:
    """Allows loading a road network graph from OSM."""

    def __init__(self, working_dir: str | Path) -> None:
        self._working_dir = Path(working_dir)

    def _get_path_for_place(self, place: str) -> Path:
        return self._working_dir / f"{hashlib.md5(place.encode()).hexdigest()}.graphml"

    def extract(self, place: str) -> nx.MultiDiGraph:
        """Load data from OSM to object. Caches data downloaded in file for future usage.

        Parameters
        ----------
        place : str
            The place to download the OSM map.

        Returns
        -------
        MultiDiGraph
            The graph downloaded from OSM.

        """
        if (path := self._get_path_for_place(place)).exists():
            return ox.load_graphml(path)

        G = ox.graph_from_place(place, network_type="drive")
        G.remove_nodes_from(list(nx.isolates(G)))
        G = G.subgraph(max(nx.strongly_connected_components(G), key=len))

        ox.save_graphml(G, path)

        return G

    def clear_cache(self, place: str) -> None:
        """Clear the betwork cache file for a given bounding box.

        Parameters
        ----------
        place : tuple
            The bounding box to download the map.

        """
        if (path := self._get_path_for_place(place)).exists():
            path.unlink()
