import sqlalchemy as db

class MySQL():
    def __init__(self, table='driven_distances', host_name='db', db_name='db', user='root', password='root', touch=False) -> None:
        self.engine = db.create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(
            host=host_name, 
            db=db_name, 
            user=user, 
            pw=password
        ))

        self.touch = touch
        self.table = table

    def load(self, df):
        df.to_sql(self.table, self.engine, index=False, if_exists='append')
        
        if self.touch:
            with open(self.touch, 'w+') as f:
                f.write('File used to control Makefile, actual data stored in DB.')