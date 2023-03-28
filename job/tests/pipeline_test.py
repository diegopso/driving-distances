import unittest, os
from ddmc.pipeline import Pipeline
from ddmc.loaders.csv import CSV
import pandas as pd

class PipelineTest(unittest.TestCase):
    def setUp(self) -> None:
        filename = 'test_data.csv'
        project_root = os.path.abspath(__file__ + "/../../..")
        self.csv_path = os.path.join(project_root, 'input', filename)
        self.output_dir = os.path.join(project_root, 'output')
        self.expected_output = os.path.join(self.output_dir, filename)

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

        if os.path.exists(self.expected_output):
            os.remove(self.expected_output)

        return super().tearDown()
    
    def test_processesData(self):
        loader = CSV(self.expected_output)
        pipe = Pipeline(file=self.csv_path, working_dir=self.output_dir, silent=True, loader=loader)
        pipe.run()
        self.assertTrue(os.path.exists(self.expected_output), 'pipeline output not saved')

        df = pd.read_csv(self.expected_output)
        self.assertEqual(len(df), 1, 'wrong number of entries evaluated')

