import unittest, os
from ddmc.loaders.csv import CSV
import pandas as pd

class CSVTest(unittest.TestCase):
    def setUp(self) -> None:
        project_root = os.path.abspath(__file__ + "/../../../..")
        self.output_path = os.path.join(project_root, 'output', 'test_data.csv')

        return super().setUp()
    
    def tearDown(self) -> None:
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

        return super().tearDown()
    
    def test_saves(self):
        loader = CSV(self.output_path)
        df = pd.DataFrame({'A': [1,2,3], 'B': [1,2,3]})
        loader.load(df)

        self.assertTrue(os.path.exists(self.output_path), 'loader didnt save file')
        
        df = pd.read_csv(self.output_path)
        self.assertEqual(len(df), 3, 'wrong data saved')

