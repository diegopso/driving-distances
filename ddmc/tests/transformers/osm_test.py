from pathlib import Path

import pandas as pd
import pytest

from ddmc.extractors.osm import OSM as OSMExtractor
from ddmc.transformers.osm import OSM


@pytest.fixture()
def coords_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "lat": [46.94610305728903, 46.94969573319538],
            "lon": [7.439152037956677, 7.446109875955413],
        }
    )


@pytest.fixture(scope="session")
def osm() -> OSM:
    extractor = OSMExtractor(Path(__file__).parent.parent / "testdata")
    G = extractor.extract("Bern, CH")
    return OSM(G)


@pytest.mark.integration
def test_converts_coordinates_to_nodes(coords_df: pd.DataFrame, osm: OSM):
    df = osm.coordinatesToNodes(coords_df, "lat", "lon")
    expected_nodes = [16268087, 379712202]
    assert len(df) == len(expected_nodes), "wrong number of rows in resulting dataframe"
    assert df["nodes"].tolist() == expected_nodes, "wrong conversion found"


@pytest.mark.integration
def test_get_driving_distances(osm: OSM):
    origins = [16268087]
    destinations = [379712202]

    df = pd.DataFrame({"o": origins, "d": destinations})
    df = osm.driving_distances(df, "o", "d")

    assert 1.7 == pytest.approx(df["km_driven"].tolist().pop(), abs=0.1)
