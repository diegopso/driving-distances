"""Module to host repositoy classes to access the DB."""

from contextlib import contextmanager
from typing import Any, Generator

import sqlalchemy as db
from sqlalchemy import BigInteger, Column, Date, Float, String
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .validator import GetDrivingDistancesRequest

Base: type = declarative_base()


class _BaseRepository:
    def __init__(self, host_name: str, db_name: str, user: str, password: str) -> None:
        self._engine = db.create_engine(
            f"mysql+pymysql://{user}:{password}@{host_name}/{db_name}"
        )

    @property
    @contextmanager
    def session(self) -> Generator[Session, Any, Any]:
        try:
            session_maker = sessionmaker(bind=self._engine, expire_on_commit=False)
            session = session_maker()
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.expunge_all()
            session.close()


class DrivenDistanceRepository(_BaseRepository):
    """Repository to access driven distances in the DB."""

    class Model(Base):
        __tablename__ = "driven_distances"
        id = Column(BigInteger, primary_key=True)
        vehicle_id = Column(String)
        day = Column(Date)
        km_driven = Column(Float)

        def format(self) -> dict:
            return {
                "vehicle_id": self.vehicle_id,
                "day": self.day,
                "km_driven": self.km_driven,
            }

    def __init__(self, host_name: str, db_name: str, user: str, password: str) -> None:
        super().__init__(host_name, db_name, user, password)
        self._model = DrivenDistanceRepository.Model

    def get_driving_distances(
        self,
        query: GetDrivingDistancesRequest | None = None,
    ) -> list[dict]:
        """Get the driving distances for a query request.

        Parameters
        ----------
        query : GetDrivingDistancesRequest
            The query parameters.

        Returns
        -------
        list[dict]
            The results found.
        """
        q = []

        if query is not None:
            if query.vehicle_id:
                q.append(self._model.vehicle_id == query.vehicle_id)

            if query.start_date is not None:
                q.append(self._model.day >= query.start_date.strftime("%Y-%m-%d"))

            if query.end_date is not None:
                q.append(self._model.day <= query.end_date.strftime("%Y-%m-%d"))

        with self.session as session:
            result = session.query(self._model).filter(*q).all()
        return [r.format() for r in result]
