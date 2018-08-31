from flask import Flask, request
from jsonschema import validate

from plot_data_listing import plot_data_listing
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

"""
Reusable JSON schema
"""
string_array_schema = {
  "type": "array",
  "items": {
    "type": "string"
  }
}
projects_schema = string_array_schema
signatures_schema = {
  "type" : "object",
  "properties": dict([(mut_type, string_array_schema) for mut_type in SIG_TYPES.keys()])
}


"""
Data listing
"""
@app.route('/data-listing', methods=['POST'])
def route_data_listing():
  output = plot_data_listing()
  return response_json(app, output)


"""
Signature plot
"""
schema_signature = {
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "sig_type": {"type": "string"}
  }
}
@app.route('/signature', methods=['POST'])
def route_signature():
  req = request.get_json(force=True)
  validate(req, schema_signature)

  output = plot_signature(name=req["name"], sig_type=req["sig_type"])
  return response_json(app, output)


"""
Exposures plot
"""
schema_exposures = {
  "type": "object",
  "properties": {
    "signatures": signatures_schema,
    "projects": projects_schema
  }
}
@app.route('/exposures', methods=['POST'])
def route_exposures():
  req = request.get_json(force=True)
  validate(req, schema_exposures)

  output = plot_signature_exposures(req["signatures"], req["projects"])
  return response_json(app, output)


"""
Exposures plot for single sample
"""
schema_exposures_single_sample = {
  "type": "object",
  "properties": {
    "signatures": signatures_schema,
    "proj_id": {"type": "string"},
    "sample_id": {"type": "string"}
  }
}
@app.route('/exposures-single-sample', methods=['POST'])
def route_exposures_single():
  req = request.get_json(force=True)
  validate(req, schema_exposures_single_sample)

  output = plot_signature_exposures(req["signatures"], [req["proj_id"]], single_sample_id=req["sample_id"])
  return response_json(app, output)


"""
Signature Genome Bins plot (Manhattan plot with bins for signature exposures)
"""
schema_signature_genome_bins = {
  "type": "object",
  "properties" : {
    "regionWidth": {"type" : "number"},
    "signatures": signatures_schema,
    "projects": projects_schema
  }
}
@app.route('/signature-genome-bins', methods=['POST'])
def route_signature_genome_bins():
  req = request.get_json(force=True)
  validate(req, schema_signature_genome_bins)

  output = plot_signature_genome_bins(req["regionWidth"], req["signatures"], req["projects"])
  return response_json(app, output)


"""
Signature Genome Bins plot for single sample
"""
schema_signature_genome_bins_single = {
  "type": "object",
  "properties": {
    "regionWidth": {"type" : "number"},
    "signatures": signatures_schema,
    "proj_id": {"type": "string"},
    "sample_id": {"type": "string"}
  }
}
@app.route('/signature-genome-bins-single-sample', methods=['POST'])
def route_signature_genome_bins_single():
  req = request.get_json(force=True)
  validate(req, schema_signature_genome_bins_single)

  output = plot_signature_genome_bins(req["regionWidth"], req["signatures"], [req["proj_id"]], single_sample_id=req["sample_id"])
  return response_json(app, output)


"""
Kataegis plot, indicators of kataegis across genome for multiple samples
"""
schema_kataegis = {
  "type": "object",
  "properties": {
    "projects": projects_schema
  }
}
@app.route('/kataegis', methods=['POST'])
def route_kataegis():
  req = request.get_json(force=True)
  validate(req, schema_kataegis)

  output = plot_kataegis(req["projects"])
  return response_json(app, output)


"""
Rainfall plot
"""
schema_rainfall = {
  "type": "object",
  "properties": {
    "proj_id": {"type": "string"},
    "sample_id": {"type": "string"}
  }
}
@app.route('/kataegis-rainfall', methods=['POST'])
def route_kataegis_rainfall():
  req = request.get_json(force=True)
  validate(req, schema_rainfall)

  output = plot_rainfall(req["proj_id"], req["sample_id"])
  return response_csv(app, output)


"""
Hierarchical clustering plot
"""
schema_clustering = {
  "type": "object",
  "properties": {
    "signatures": signatures_schema,
    "projects": projects_schema
  }
}
@app.route('/clustering', methods=['POST'])
def route_clustering():
  req = request.get_json(force=True)
  validate(req, schema_clustering)

  output = plot_clustering(req["signatures"], req["projects"])
  return response_json(app, output)


"""
Samples with signatures plot
"""
schema_samples_with_signatures = {
  "type": "object",
  "properties": {
    "signatures": signatures_schema,
    "projects": projects_schema
  }
}
@app.route('/samples-with-signatures', methods=['POST'])
def route_samples_with_signatures():
  req = request.get_json(force=True)
  validate(req, schema_samples_with_signatures)

  output = plot_samples_with_signatures(req["signatures"], req["projects"])
  return response_json(app, output)


"""
Karyotype plot (chromosome bands)
"""
@app.route('/karyotype', methods=['POST'])
def route_karyotype():
  output = plot_karyotypes()
  return response_csv(app, output)


if __name__ == '__main__':
  app.run(
      host='0.0.0.0',
      debug=bool(os.environ.get('DEBUG', '')), 
      port=int(os.environ.get('PORT', 8000)),
      use_reloader=True
  )
