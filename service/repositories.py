import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, String, Date, Float

Base = declarative_base()

class BaseRepository:
    def __init__(self, host_name='db', db_name='db', user='root', password='root') -> None:
        self.engine = db.create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(
            host=host_name, 
            db=db_name, 
            user=user, 
            pw=password
        ))

    def get_session(self):
        session_maker = db.orm.sessionmaker(bind=self.engine)
        session = session_maker()
        Base.metadata.create_all(self.engine)
        return session

class DrivenDistanceRepository(BaseRepository):
    class Model(Base):
        __tablename__ = 'driven_distances'
        id = Column(BigInteger, primary_key=True)
        vehicle_id = Column(String)
        day = Column(Date)
        km_driven = Column(Float)

        def format(self) -> dict:
            return {
                "vehicle_id": self.vehicle_id,
                "day": self.day,
                "km_driven": self.km_driven
            }

    def __init__(self, host_name='db', db_name='db', user='root', password='root') -> None:
        super().__init__(host_name, db_name, user, password)
        self.model = DrivenDistanceRepository.Model

    def getDrivingDistances(self, vehicleId=None, startDate=None, endDate=None):
        q = []
        
        if vehicleId is not None:
            q.append(self.model.vehicle_id == vehicleId)

        if startDate is not None:
            q.append(self.model.day >= startDate)
        
        if endDate is not None:
            q.append(self.model.day <= endDate)

        result = self.get_session().query(self.model).filter(*q).all()
        return [r.format() for r in result]
