import hashlib
from pathlib import Path

import networkx as nx  # type: ignore[import-untyped]
import osmnx as ox
import pytest

from ddmc.extractors.osm import OSM


class Counter:
    def __init__(self):
        self.count = 0

    def __call__(self, *_, **__):
        self.count += 1
        G = nx.MultiDiGraph()
        for u, v in [(0, 1), (1, 0), (1, 2), (2, 1)]:
            G.add_edge(u, v)
        return G


@pytest.fixture()
def osm_config(tmp_path: Path) -> tuple[str, Path]:
    place = "Bern, CH"
    filename = f"{hashlib.md5(place.encode()).hexdigest()}.graphml"
    return place, tmp_path / filename


def test_loads_new_data(
    osm_config: tuple[str, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    place, expected_path = osm_config
    extractor = OSM(working_dir=tmp_path)

    counter = Counter()
    monkeypatch.setattr(ox, "graph_from_place", counter)
    extractor.extract(place)

    assert counter.count == 1, "graph not downloaded"
    assert expected_path.is_file(), "graph not saved"


def test_loads_existing_data(
    osm_config: tuple[str, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    place, _ = osm_config
    extractor = OSM(working_dir=tmp_path)

    counter = Counter()
    monkeypatch.setattr(ox, "graph_from_place", counter)

    # make sure data exists
    extractor.extract(place)

    # call again to check for cache usage
    extractor.extract(place)

    assert counter.count == 1


def test_deletes_cache_file(
    osm_config: tuple[str, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    place, expected_path = osm_config
    extractor = OSM(working_dir=tmp_path)

    monkeypatch.setattr(ox, "graph_from_place", Counter())

    extractor.extract(place)
    assert expected_path.exists()

    extractor.clear_cache(place)
    assert not expected_path.exists()
