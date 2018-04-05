import json
from flask import Flask
from web_constants import *

def response_csv(app, output):
    return app.response_class(
        response=output,
        status=200,
        mimetype='text/csv',
        headers=HEADERS
    )

def response_json(app, output):
    return app.response_class(
        response=json.dumps(output),
        status=200,
        mimetype='application/json',
        headers=HEADERS
    )