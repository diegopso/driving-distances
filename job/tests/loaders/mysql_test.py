import unittest, os
from ddmc.loaders.mysql import MySQL
import pandas as pd
import sqlalchemy as db

class MySQLTest(unittest.TestCase):
    def setUp(self) -> None:
        project_root = os.path.abspath(__file__ + "/../../../..")
        self.touch_path = os.path.join(project_root, 'output', 'test_driven_distances.out')

        self.table_name = 'test_driven_distances'

        self.engine = db.create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(
            host='db', 
            db='db', 
            user='root', 
            pw='root'
        ))

        sql = " ".join([
            "CREATE TABLE %s (" % self.table_name,
                "`id` BIGINT NOT NULL AUTO_INCREMENT,",
                "`vehicle_id` VARCHAR(255) NOT NULL,",
                "`day` DATE NOT NULL,",
                "`km_driven` FLOAT NOT NULL,",
                "PRIMARY KEY (id)",
            ");",
        ])

        with self.engine.connect() as con:
            statement = db.sql.text(sql)
            con.execute(statement)

        return super().setUp()
    
    def tearDown(self) -> None:
        with self.engine.connect() as con:
            statement = db.sql.text("DROP TABLE %s;" % self.table_name)
            con.execute(statement)
        
        if os.path.exists(self.touch_path):
            os.remove(self.touch_path)

        return super().tearDown()
    
    def test_savesToDB(self):
        loader = MySQL(table=self.table_name, touch=self.touch_path)

        df = pd.DataFrame({
            "vehicle_id": ["bern-1", "bern-2"],
            "day": ["2019-05-31", "2019-05-31"],
            "km_driven": [6.852044743674312, 5.349171694607154]
        })

        loader.load(df)

        with self.engine.connect() as con:
            statement = db.sql.text("SELECT count(id) from %s;" % self.table_name)
            result = con.execute(statement).scalar()

        self.assertEqual(result, 2, 'no results saved')
        self.assertTrue(os.path.exists(self.touch_path), 'flag file not created')

