import os
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table

def db_connect(local=True):
    # TODO: set local to False by default
    if local:
        engine = create_engine("mysql://{user}:{password}@localhost:3306/explosig?unix_socket=/Applications/MAMP/tmp/mysql/mysql.sock".format(
            user='root',
            password='root'
        ))
    else:
        engine = create_engine("mysql://{user}:{password}@db:3306/explosig".format(
            user=os.environ['EXPLOSIG_DB_USER'],
            password=os.environ['EXPLOSIG_DB_PASSWORD']
        ))
    conn = engine.connect()
    return engine, conn

def table_connect(table_name):
    engine, conn = db_connect()
    metadata = MetaData(engine, reflect=True)
    table = metadata.tables[table_name]
    return table, conn