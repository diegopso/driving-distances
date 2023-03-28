import unittest, os, hashlib
import pandas as pd
from ddmc.transformers.osm import OSM
from ddmc.extractors.osm import OSM as OSMExtractor

class OSMTest(unittest.TestCase):
    def setUp(self) -> None:
        project_root = os.path.abspath(__file__ + "/../../../..")
        self.output_dir = os.path.join(project_root, 'output')

        self.bbox = (47.0786, 46.8332, 7.5957, 7.2869)
        extractor = OSMExtractor(self.output_dir)
        G = extractor.extract(self.bbox)

        self.osm = OSM(G)
        
        self.coords_df = pd.DataFrame({
            "lat": [46.94610305728903, 46.94969573319538],
            "lon": [7.439152037956677, 7.446109875955413]
        })

        self.expected_nodes = [16268087, 379712202]
        self.expected_distances = [1.7]

        return super().setUp()
    
    def tearDown(self) -> None:
        extractor = OSMExtractor(self.output_dir)
        extractor.clearCache(self.bbox)
        return super().tearDown()

    def test_convertsCoordinatesToNodes(self):
        df = self.osm.coordinatesToNodes(self.coords_df, 'lat', 'lon')

        self.assertEqual(len(df), len(self.expected_nodes), 'wrong number of rows in resulting dataframe')
        self.assertListEqual(df['nodes'].tolist(), self.expected_nodes, 'wrong conversion found')

    def test_getDrivingDistances(self):
        origins = self.expected_nodes.copy()
        origins.pop()
        destinations = self.expected_nodes.copy()
        destinations.pop(0)

        df = pd.DataFrame({
            'o': origins,
            'd': destinations
        })

        df = self.osm.drivingDistances(df, 'o', 'd')
        
        bag = zip(self.expected_distances, df['km_driven'].tolist())
        for (expected, evaluated) in bag:
            self.assertAlmostEqual(expected, evaluated, msg='wrong distance evaluated', delta=0.1)

