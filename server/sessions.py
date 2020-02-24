import os
import uuid
import json
import pandas as pd
from db import table_connect
import requests
import websockets
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosed
from web_constants import EXPLOSIG_CONNECT_HOST

def session_get(slug):
    table, conn = table_connect('session')

    sel = table.select().where(table.c.slug == slug)
    res = conn.execute(sel)
    row = res.fetchone()

    return { "state": json.loads(row['data']) }

def session_start(state):
    table, conn = table_connect('session')

    slug = str(uuid.uuid4())[:8]
    ins = table.insert().values(slug=slug, data=json.dumps(state))
    conn.execute(ins)

    return { "slug": slug }

async def session_connect(websocket_in):
    await websocket_in.accept()
    init_json = await websocket_in.receive_json()
    url = 'ws://' + EXPLOSIG_CONNECT_HOST + '/global-session-connect'
    async with websockets.connect(url) as websocket_out:
        await websocket_out.send(json.dumps(init_json))
        while True:
            try:
                data = json.loads(await websocket_out.recv())
                try:
                    await websocket_in.send_json(data)
                except ConnectionClosed:
                    break
            except WebSocketDisconnect:
                break

async def session_post(session_id, data):
    url = 'http://' + EXPLOSIG_CONNECT_HOST + '/global-session-post'
    payload = { 'data': data, 'session_id': session_id }
    r = requests.post(url, data=json.dumps(payload))
    r.raise_for_status()
    return r.json()