import unittest, os
from ddmc.extractors.default_extractor import DefaultExtractor

class DefaultExtractorTest(unittest.TestCase):
    def setUp(self) -> None:
        project_root = os.path.abspath(__file__ + "/../../../..")
        self.csv_path = os.path.join(project_root, 'input/test_data.csv')

        txt = "\n".join([
            '"vehicle_id","location_raw_lat","location_raw_lon","created_timestamp"',
            '"bern-1",46.94083234438826,7.419139400426145,"2023-03-28 09:33:54+00"',
            '"bern-1",46.94610305728903,7.439152037956677,"2023-03-28 09:27:12+00"',
            '"bern-1",46.94969573319538,7.446109875955413,"2023-03-28 09:16:16+00"',
            '"bern-1",46.9494144717443,7.455317604797753,"2023-03-28 09:12:02+00"',
        ])

        with open(self.csv_path, "w+") as file:
            file.write(txt)

        return super().setUp()
    
    def tearDown(self) -> None:
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)

        return super().tearDown()
    
    def test_loadsData(self):
        extractor = DefaultExtractor()
        df = extractor.extract(self.csv_path)

        self.assertEqual(df['location_raw_lat'].dtype, 'float64', 'lat column not imported as float')
        self.assertEqual(df['location_raw_lon'].dtype, 'float64', 'lon column not imported as float')
        self.assertEqual(len(df), 4, 'wrong number of lines imported')

