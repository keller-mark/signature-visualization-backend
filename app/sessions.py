import os
import uuid
import json
import pandas as pd
from db import connect
from starlette.websockets import WebSocketDisconnect

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

open_websockets = {}
async def session_connect(new_websocket):
    global open_websockets
    await new_websocket.accept()
    init_json = await new_websocket.receive_json()
    # Store websocket connections in the global dict based on the connection ID
    try:
        open_websockets[init_json["session_id"]].append(new_websocket)
    except KeyError:
        open_websockets[init_json["session_id"]] = [ new_websocket ]
    # Keep the connections open by pretending to wait for json
    try:
        await new_websocket.receive_json()
    except WebSocketDisconnect:
        del open_websockets[init_json["session_id"]]

async def session_post(session_id, data):
    global open_websockets
    try:
        for open_ws in open_websockets[session_id]:
            await open_ws.send_json({ 'data': data })
    except KeyError:
        return {"result": "No open websockets for that connection ID."}
    return {}