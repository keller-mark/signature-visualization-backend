from starlette.applications import Starlette
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
  try:
    app.open_websockets[init_json["session_id"]].append(websocket)
  except KeyError:
    app.open_websockets[init_json["session_id"]] = [ websocket ]
  try:
    # Keep the connections open by pretending to wait for json
    await websocket.receive_json()
  except WebSocketDisconnect:
    app.open_websockets[init_json["session_id"]]

@app.route('/global-session-post', methods=['POST'])
async def route_global_session_post(request):
  req = await request.json()
  session_id = req["session_id"]
  data = req["data"]
  try:
    for open_ws in app.open_websockets[session_id]:
      await open_ws.send_json({ 'data': data })
    return response_json(app, {"message": "Success!"})
  except KeyError:
    return response_json_error(app, {"message": "No open websockets for that connection ID."}, 500)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8200)))