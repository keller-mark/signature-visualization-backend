import uuid
import json
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, Integer, String, Text

def connect():
    engine = create_engine('mysql://imuse:imuse@db:3306/imuse')
    conn = engine.connect()
    metadata = MetaData(engine, reflect=True)
    table = metadata.tables['sharing']
    return table, conn

def get_sharing_state(slug):
    table, conn = connect()

    sel = table.select().where(table.c.slug == slug)
    res = conn.execute(sel)
    row = res.fetchone()

    return { "state": json.loads(row['data']) }

def set_sharing_state(state):
    table, conn = connect()

    slug = str(uuid.uuid4())[:8]
    ins = table.insert().values(slug=slug, data=json.dumps(state))
    conn.execute(ins)

    return { "slug": slug }
