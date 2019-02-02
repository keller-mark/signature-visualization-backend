import uuid
import json
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, Integer, String, Text

from web_constants import META_FEATURED_FILE

def connect():
    engine = create_engine('mysql://explosig:explosig@db:3306/explosig')
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

def plot_featured_listing():
    df = pd.read_csv(META_FEATURED_FILE, sep="\t")
    df = df.fillna(value="")
    return df.to_dict('records')