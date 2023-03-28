import pandas as pd

class DefaultExtractor():
    def extract(self, file : str) -> pd.DataFrame:
        """Loads a CSV file into a dataframe, also parses the column `created_timestamp` into Datetime and adjusts the timezone."""
        df = pd.read_csv(file, parse_dates=['created_timestamp'], dtype={
            'vehicle_id': str,
            'location_raw_lat': float,
            'location_raw_lon': float,
        })

        df['created_timestamp'] = df['created_timestamp'].dt.tz_convert(tz='Europe/Berlin')
        df['created_timestamp'] = df['created_timestamp'].dt.date
        
        return df