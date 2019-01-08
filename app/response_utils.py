import json
from flask import Flask

HEADERS = { 'Access-Control-Allow-Origin': '*' }

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

def response_json_error(app, output, status):
    return app.response_class(
        response=json.dumps(output),
        status=status,
        mimetype='application/json',
        headers=HEADERS
    )