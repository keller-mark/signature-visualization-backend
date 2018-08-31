from flask import Flask, request
from jsonschema import validate

from plot_signature import plot_signature
from plot_karyotypes import plot_karyotypes
from plot_data_listing import plot_data_listing
from plot_clustering import plot_clustering
from plot_kataegis import plot_kataegis
from plot_rainfall import plot_rainfall
from plot_samples_with_signatures import plot_samples_with_signatures
from plot_signature_exposures import plot_signature_exposures
from plot_signature_genome_bins import plot_signature_genome_bins

from web_constants import *
from response_utils import *

app = Flask(__name__)

projects_schema = {
  "type": "array",
  "items": {
    "type": "string"
  }
}

signatures_schema = {
  "type" : "object",
  "properties": {
    "SBS": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "DBS": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "INDEL": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}

@app.route('/signature-genome-bins', methods=['POST'])
def route_signature_genome_bins():
  req = request.get_json(force=True)
  schema = {
    "type": "object",
    "properties" : {
      "regionWidth": {"type" : "number"},
      "signatures": signatures_schema,
      "projects": projects_schema
    }
  }
  validate(req, schema)

  output = plot_signature_genome_bins(req["regionWidth"], req["signatures"], req["projects"])
  return response_json(app, output)

@app.route('/signature-genome-bins-single-sample', methods=['POST'])
def route_signature_genome_bins_single():
  req = request.get_json(force=True)
  schema = {
    "type": "object",
    "properties": {
      "regionWidth": {"type" : "number"},
      "signatures": signatures_schema,
      "proj_id": {"type": "string"},
      "sample_id": {"type": "string"}
    }
  }
  validate(req, schema)

  output = plot_signature_genome_bins(req["regionWidth"], req["signatures"], [req["proj_id"]], single_sample_id=req["sample_id"])
  return response_json(app, output)

@app.route('/kataegis', methods=['POST'])
def route_kataegis():
  req = request.get_json(force=True)
  schema = {
    "type": "object",
    "properties": {
      "projects": projects_schema
    }
  }
  validate(req, schema)

  output = plot_kataegis(req["projects"])
  return response_json(app, output)

@app.route('/kataegis-rainfall', methods=['POST'])
def route_kataegis_rainfall():
  req = request.get_json(force=True)
  schema = {
    "type": "object",
    "properties": {
      "proj_id": {"type": "string"},
      "sample_id": {"type": "string"}
    }
  }
  validate(req, schema)

  output = plot_rainfall(req["proj_id"], req["sample_id"])
  return response_csv(app, output)

@app.route('/exposures', methods=['POST'])
def route_exposures():
  req = request.get_json(force=True)
  schema = {
    "type": "object",
    "properties": {
      "signatures": signatures_schema,
      "projects": projects_schema
    }
  }
  validate(req, schema)

  output = plot_signature_exposures(req["signatures"], req["projects"])
  return response_json(app, output)

@app.route('/exposures-single-donor', methods=['POST'])
def route_exposures_single():
  req = request.get_json(force=True)
  schema = {
    "type": "object",
    "properties": {
      "signatures": signatures_schema,
      "proj_id": {"type": "string"},
      "sample_id": {"type": "string"}
    }
  }
  validate(req, schema)

  output = plot_signature_exposures(req["signatures"], [req["proj_id"]], single_sample_id=req["sample_id"])
  return response_json(app, output)

@app.route('/signature', methods=['POST'])
def route_signature():
  req = request.get_json(force=True)
  schema = {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "sig_type": {"type": "string"}
    }
  }
  validate(req, schema)

  output = plot_signature(name=req["name"], sig_type=req["sig_type"])
  return response_json(app, output)

@app.route('/data-listing', methods=['POST'])
def route_data_listing():
  output = plot_data_listing()
  return response_json(app, output)

@app.route('/karyotype', methods=['POST'])
def route_karyotype():
  output = plot_karyotypes()
  return response_csv(app, output)

@app.route('/samples-with-signatures', methods=['POST'])
def route_samples_with_signatures():
  req = request.get_json(force=True)
  schema = {
    "type": "object",
    "properties": {
      "signatures": signatures_schema,
      "projects": projects_schema
    }
  }
  validate(req, schema)

  output = plot_samples_with_signatures(req["signatures"], req["projects"])
  return response_json(app, output)

@app.route('/clustering', methods=['POST'])
def route_clustering():
  req = request.get_json(force=True)
  schema = {
    "type": "object",
    "properties": {
      "signatures": signatures_schema,
      "projects": projects_schema
    }
  }
  validate(req, schema)

  output = plot_clustering(req["signatures"], req["projects"])
  return response_json(app, output)

if __name__ == '__main__':
  app.run(
      host='0.0.0.0',
      debug=bool(os.environ.get('DEBUG', '')), 
      port=int(os.environ.get('PORT', 8000)),
      use_reloader=True
  )
