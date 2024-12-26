from typing import Protocol

import pandas as pd


class Loader(Protocol):
    def load(self, df: pd.DataFrame) -> None:
        """Save data to MySQL.

        Parameters
        ----------
        df : DataFrame
            The dataframe to be saved.

        """
