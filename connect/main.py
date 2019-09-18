from starlette.applications import Starlette
from starlette.websockets import WebSocketDisconnect
import uvicorn
import os
from response_utils import *

app = Starlette(debug=bool(os.environ.get('DEBUG', '')))
app.open_websockets = {}

@app.websocket_route('/global-session-connect')
async def route_global_session_connect(websocket):
  await websocket.accept()
  init_json = await websocket.receive_json()
  # Store websocket connections in the global dict based on the connection ID
  if "session_id" in init_json.keys():
    session_id = init_json["session_id"]
    if len(session_id) != 8:
      # Wrong format for session ID
      print("Received an incorrectly-formatted session ID")
      return
    if session_id in app.open_websockets.keys():
      if len(app.open_websockets[session_id]) < 25:
        app.open_websockets[session_id].append(websocket)
      else:
        # Too many websockets open for this session
        print("Max number of websockets reached for session with ID %s" % session_id)
        return
    else:
      app.open_websockets[session_id] = [ websocket ]

    while True:
      try:
        # Keep the connections open by pretending to wait for json
        await websocket.receive_json()
      except WebSocketDisconnect:
        app.open_websockets[session_id].remove(websocket)
        if len(app.open_websockets[session_id]) == 0:
          del app.open_websockets[session_id]
        break

@app.route('/global-session-post', methods=['POST'])
async def route_global_session_post(request):
  req = await request.json()
  session_id = req["session_id"]
  data = req["data"]
  if session_id in app.open_websockets.keys():
    for open_ws in app.open_websockets[session_id]:
      await open_ws.send_json(data)
    return response_json(app, { "message": ("Sent data to %d open client websockets." % len(app.open_websockets[session_id])) })
  else:
    return response_json_error(app, { "message": "No open websockets for that session ID." }, 500)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8200)))