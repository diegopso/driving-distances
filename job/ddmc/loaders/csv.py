import csv

class CSV():
    def __init__(self, output_path : str) -> None:
        self.output_path = output_path

    def load(self, df):
        """Saves the data to a CSV file."""
        df.to_csv(self.output_path, index=False, quoting=csv.QUOTE_NONNUMERIC)