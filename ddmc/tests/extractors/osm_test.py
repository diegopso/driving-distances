import re
from pathlib import Path

import networkx as nx  # type: ignore[import-untyped]
import osmnx as ox
import pytest

from ddmc.extractors.osm import OSM, BoundingBox


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
def osm_config(tmp_path: Path) -> tuple[BoundingBox, Path]:
    bbox = BoundingBox(7.2869, 46.8332, 7.5957, 47.0786)
    filename = f"{bbox.hash}.graphml"
    return bbox, tmp_path / filename


def test_cant_create_invalid_bbox():
    with pytest.raises(ValueError, match="right must be greater than left"):
        BoundingBox(1, 1, 1, 2)

    with pytest.raises(ValueError, match="top must be greater than bottom"):
        BoundingBox(1, 1, 2, 1)


def test_formats_bbox():
    probe = BoundingBox(1.999, 1.999, 1.9999, 1.9999)
    assert probe != probe.formated
    assert probe.formated == BoundingBox(1.99, 1.99, 2, 2)


def test_hashes_bbox():
    probe = BoundingBox(1.999, 1.999, 1.9999, 1.9999).hash
    assert bool(re.match(r"^[a-fA-F0-9]{32}$", probe))


def test_plain_str():
    probe = BoundingBox(1.999, 1.999, 1.9999, 1.9999)
    assert str(probe) == "(1.99, 1.99, 2.0, 2.0)"


def test_loads_new_data(
    osm_config: tuple[BoundingBox, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    bbox, expected_path = osm_config
    extractor = OSM(working_dir=tmp_path)

    counter = Counter()
    monkeypatch.setattr(ox, ox.graph_from_bbox.__name__, counter)
    extractor.extract(bbox)

    assert counter.count == 1, "graph not downloaded"
    assert expected_path.is_file(), "graph not saved"


def test_loads_existing_data(
    osm_config: tuple[BoundingBox, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    place, _ = osm_config
    extractor = OSM(working_dir=tmp_path)

    counter = Counter()
    monkeypatch.setattr(ox, ox.graph_from_bbox.__name__, counter)

    # make sure data exists
    extractor.extract(place)

    # call again to check for cache usage
    extractor.extract(place)

    assert counter.count == 1


def test_deletes_cache_file(
    osm_config: tuple[BoundingBox, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    place, expected_path = osm_config
    extractor = OSM(working_dir=tmp_path)

    monkeypatch.setattr(ox, "graph_from_bbox", Counter())

    extractor.extract(place)
    assert expected_path.exists()

    extractor.clear_cache(place)
    assert not expected_path.exists()
