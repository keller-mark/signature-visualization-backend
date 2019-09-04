import os
import uuid
import json
import pandas as pd
from db import connect
import requests
import websockets
from starlette.websockets import WebSocketDisconnect
from web_constants import EXPLOSIG_CONNECT_HOST

def session_get(session_id):
    table, conn = connect('sessions')

    sel = table.select().where(table.c.session_id == session_id)
    res = conn.execute(sel)
    row = res.fetchone()

    return { "state": json.loads(row['data']) }

def session_start(state):
    table, conn = connect('sessions')

    session_id = str(uuid.uuid4())[:8]
    ins = table.insert().values(session_id=session_id, data=json.dumps(state))
    conn.execute(ins)

    return { "session_id": session_id }

async def session_connect(websocket_in):
    await websocket_in.accept()
    init_json = await websocket_in.receive_json()
    url = 'ws://' + EXPLOSIG_CONNECT_HOST + '/global-session-connect'
    async with websockets.connect(url) as websocket_out:
        await websocket_out.send(json.dumps(init_json))
        data = json.loads(await websocket_out.recv())
        try:
            await websocket_in.send_json(data)
            # Keep the connections open by pretending to wait for json
            await websocket_in.receive_json()
        except WebSocketDisconnect:
            pass

async def session_post(session_id, data):
    url = 'http://' + EXPLOSIG_CONNECT_HOST + '/global-session-post'
    payload = { 'data': data, 'session_id': session_id }
    r = requests.post(url, data=json.dumps(payload))
    r.raise_for_status()
    return {"message": "Success"}