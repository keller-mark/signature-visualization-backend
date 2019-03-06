import json
from starlette.responses import JSONResponse

HEADERS = { 'Access-Control-Allow-Origin': '*' }

def response_json(app, output):
    return JSONResponse(
        content=output,
        status_code=200,
        headers=HEADERS
    )

def response_json_error(app, output, status):
    return JSONResponse(
        content=output,
        status_code=status,
        headers=HEADERS
    )