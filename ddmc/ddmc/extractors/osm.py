"""Module to handle loading OSM data and converting into grphs."""

from __future__ import annotations

import hashlib
import math
from dataclasses import astuple, dataclass
from functools import cached_property
from pathlib import Path

import networkx as nx  # type: ignore [import-untyped]
import osmnx as ox


def _ceil(n: float) -> float:
    return math.ceil(n * 100) / 100


def _floor(n: float) -> float:
    return math.floor(n * 100) / 100


@dataclass(frozen=True)
class BoundingBox:
    left: float
    bottom: float
    right: float
    top: float

    def __post_init__(self):
        if self.right <= self.left:
            raise ValueError("right must be greater than left")

        if self.top <= self.bottom:
            raise ValueError("top must be greater than bottom")

    @cached_property
    def formated(self) -> BoundingBox:
        return BoundingBox(
            left=_floor(self.left),
            bottom=_floor(self.bottom),
            right=_ceil(self.right),
            top=_ceil(self.top),
        )

    @cached_property
    def hash(self):
        return f"{hashlib.md5(str(self.formated).encode()).hexdigest()}"

    def __str__(self):
        return str(astuple(self.formated))


class OSM:
    """Allows loading a road network graph from OSM."""

    def __init__(self, working_dir: str | Path) -> None:
        self._working_dir = Path(working_dir)

    def _get_path(self, identifier: str) -> Path:
        return self._working_dir / f"{identifier}.graphml"

    def extract(self, bbox: BoundingBox) -> nx.MultiDiGraph:
        """Load data from OSM to object. Caches data downloaded in file for future usage.

        Parameters
        ----------
        bbox : BoundingBox
            The bbox to download the OSM map.

        Returns
        -------
        MultiDiGraph
            The graph downloaded from OSM.

        """
        if (path := self._get_path(bbox.hash)).exists():
            return ox.load_graphml(path)

        G = ox.graph_from_bbox(astuple(bbox.formated), network_type="drive")
        G.remove_nodes_from(list(nx.isolates(G)))
        G = G.subgraph(max(nx.strongly_connected_components(G), key=len))

        ox.save_graphml(G, path)

        return G

    def clear_cache(self, bbox: BoundingBox) -> None:
        """Clear the betwork cache file for a given bounding box.

        Parameters
        ----------
        bbox : BoundingBox
            The bounding box to download the map.

        """
        if (path := self._get_path(bbox.hash)).exists():
            path.unlink()
