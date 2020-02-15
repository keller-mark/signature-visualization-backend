import os
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table

def connect(table_name):
    engine = create_engine("mysql://{user}:{password}@db:3306/explosig".format(
      user=os.environ['EXPLOSIG_DB_USER'],
      password=os.environ['EXPLOSIG_DB_PASSWORD']
    ))
    conn = engine.connect()
    metadata = MetaData(engine, reflect=True)
    table = metadata.tables[table_name]
    return table, conn