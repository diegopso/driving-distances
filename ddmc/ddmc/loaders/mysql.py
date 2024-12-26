"""Module to host classes to handle connection and data loading to MySQL."""

import pandas as pd
import sqlalchemy as db


class MySQL:
    """Allow loading data to MySQL DB."""

    def __init__(
        self,
        table: str = "driven_distances",
        host_name: str = "db",
        db_name: str = "db",
        user: str = "root",
        password: str = "root",
    ) -> None:
        self._engine = db.create_engine(
            f"mysql+pymysql://{user}:{password}@{host_name}/{db_name}"
        )

        self._table = table

    def load(self, df: pd.DataFrame) -> None:
        """Save data to MySQL.

        Parameters
        ----------
        df : DataFrame
            The dataframe to be saved.

        """
        df.to_sql(self._table, self._engine, index=False, if_exists="append")
