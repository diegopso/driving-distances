import unittest, os
from ddmc.extractors.osm import OSM

class OSMTest(unittest.TestCase):
    def setUp(self) -> None:
        project_root = os.path.abspath(__file__ + "/../../../..")
        self.working_dir = os.path.join(project_root, 'output')
        self.bbox = (47.0786, 46.8332, 7.5957, 7.2869)
        
        filename = '%d.graphml' % abs(hash(self.bbox))
        self.expected_path = os.path.join(self.working_dir, filename)

        return super().setUp()
    
    def tearDown(self) -> None:
        extractor = OSM(working_dir=self.working_dir)
        extractor.clearCache(self.bbox)
        return super().tearDown()
    
    def test_loadsData(self):
        extractor = OSM(working_dir=self.working_dir)
        extractor.extract(self.bbox)
        self.assertTrue(os.path.isfile(self.expected_path), 'graph not saved')

