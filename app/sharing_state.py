import os
import uuid
import json
import pandas as pd
from db import connect

from web_constants import META_FEATURED_FILE

def get_sharing_state(slug):
    table, conn = connect('sharing')

    sel = table.select().where(table.c.slug == slug)
    res = conn.execute(sel)
    row = res.fetchone()

    return { "state": json.loads(row['data']) }

def set_sharing_state(state):
    table, conn = connect('sharing')

    slug = str(uuid.uuid4())[:8]
    ins = table.insert().values(slug=slug, data=json.dumps(state))
    conn.execute(ins)

    return { "slug": slug }

def plot_featured_listing():
    df = pd.read_csv(META_FEATURED_FILE, sep="\t")
    df = df.fillna(value="")
    return df.to_dict('records')