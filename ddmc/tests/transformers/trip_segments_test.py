import datetime

import pandas as pd

from ddmc.transformers.trip_segments import TripSegments


def test_identifies_trip_segments():
    df = pd.DataFrame(
        {
            "vehicle_id": [
                "bern-1",
                "bern-2",
                "bern-1",
                "bern-2",
                "bern-1",
                "bern-2",
                "bern-1",
                "bern-2",
                "bern-1",
            ],
            "nodes": [
                1,
                2,
                3,
                4,
                3,
                5,
                3,
                6,
                3,
            ],
            "created_timestamp": [
                datetime.datetime(2023, 3, 31),
                datetime.datetime(2023, 3, 31),
                datetime.datetime(2023, 3, 31),
                datetime.datetime(2023, 3, 31),
                datetime.datetime(2023, 3, 31),
                datetime.datetime(2023, 3, 31),
                datetime.datetime(2023, 3, 20),
                datetime.datetime(2023, 3, 31),
                datetime.datetime(2023, 3, 20),
            ],
        }
    )

    extractor = TripSegments()
    result = extractor.identify(df)

    assert len(result) == 6, "wrong number of trip segments identified"
