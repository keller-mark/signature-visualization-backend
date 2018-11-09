from flask import Flask, request
from jsonschema import validate

from plot_data_listing import plot_data_listing
""" from plot_signature import plot_signature
from plot_karyotypes import plot_karyotypes """
from plot_data_listing import plot_data_listing
from plot_clustering import plot_clustering
""" from plot_kataegis import plot_kataegis
from plot_rainfall import plot_rainfall """
from plot_samples_with_signatures import plot_samples_with_signatures

""" from plot_signature_genome_bins import plot_signature_genome_bins
from plot_genome_event_track import plot_genome_event_track, autocomplete_gene """
from scale_samples import scale_samples

from plot_exposures import plot_exposures
from scale_exposures import scale_exposures

from plot_counts import plot_counts
from scale_counts import scale_counts

from plot_samples_meta import plot_samples_meta


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
  "properties": dict([(mut_type, string_array_schema) for mut_type in MUT_TYPES])
}


"""
Data listing
"""
@app.route('/data-listing', methods=['POST'])
def route_data_listing():
  output = plot_data_listing()
  return response_json(app, output)


"""
Signatures
"""
""" schema_signature = {
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "mut_type": {"type": "string"}
  }
}
@app.route('/signature', methods=['POST'])
def route_signature():
  req = request.get_json(force=True)
  validate(req, schema_signature)

  assert(req["mut_type"] in SIG_TYPES.keys())

  output = plot_signature(name=req["name"], sig_type=SIG_TYPES[req["mut_type"]])
  return response_json(app, output) """

"""
Samples-by-project
"""
schema_samples_meta = {
  "type": "object",
  "properties": {
    "projects": string_array_schema
  }
}
@app.route('/plot-samples-meta', methods=['POST'])
def route_plot_samples_meta():
  req = request.get_json(force=True)
  validate(req, schema_counts)

  output = plot_samples_meta(req["projects"])
  return response_json(app, output)

"""
Counts
"""
schema_counts = {
  "type": "object",
  "properties": {
    "projects": string_array_schema
  }
}
@app.route('/plot-counts', methods=['POST'])
def route_plot_counts():
  req = request.get_json(force=True)
  validate(req, schema_counts)

  output = plot_counts(req["projects"])
  return response_json(app, output)

@app.route('/scale-counts', methods=['POST'])
def route_scale_counts():
  req = request.get_json(force=True)
  validate(req, schema_counts)

  output = scale_counts(req["projects"])
  return response_json(app, output)

@app.route('/scale-counts-sum', methods=['POST'])
def route_scale_counts_sum():
  req = request.get_json(force=True)
  validate(req, schema_counts)

  output = scale_counts(req["projects"], count_sum=True)
  return response_json(app, output)

"""
Exposures
"""
schema_exposures = {
  "type": "object",
  "properties": {
    "signatures": string_array_schema,
    "projects": string_array_schema,
    "mut_type": {"type": "string"}
  }
}
@app.route('/plot-exposures', methods=['POST'])
def route_plot_exposures():
  req = request.get_json(force=True)
  validate(req, schema_exposures)

  assert(req["mut_type"] in SIG_TYPES.keys())

  output = plot_exposures(req["signatures"], req["projects"], req["mut_type"])
  return response_json(app, output)

@app.route('/plot-exposures-normalized', methods=['POST'])
def route_plot_exposures_normalized():
  req = request.get_json(force=True)
  validate(req, schema_exposures)

  assert(req["mut_type"] in SIG_TYPES.keys())

  output = plot_exposures(req["signatures"], req["projects"], req["mut_type"], exp_normalize=True)
  return response_json(app, output)

@app.route('/scale-exposures', methods=['POST'])
def route_scale_exposures():
  req = request.get_json(force=True)
  validate(req, schema_exposures)

  assert(req["mut_type"] in SIG_TYPES.keys())

  output = scale_exposures(req["signatures"], req["projects"], req["mut_type"], exp_sum=False)
  return response_json(app, output)

@app.route('/scale-exposures-normalized', methods=['POST'])
def route_scale_exposures_normalized():
  req = request.get_json(force=True)
  validate(req, schema_exposures)

  assert(req["mut_type"] in SIG_TYPES.keys())

  output = scale_exposures(req["signatures"], req["projects"], req["mut_type"], exp_sum=False, exp_normalize=True)
  return response_json(app, output)


@app.route('/scale-exposures-sum', methods=['POST'])
def route_scale_exposures_sum():
  req = request.get_json(force=True)
  validate(req, schema_exposures)

  assert(req["mut_type"] in SIG_TYPES.keys())

  output = scale_exposures(req["signatures"], req["projects"], req["mut_type"], exp_sum=True)
  return response_json(app, output)


"""
Exposures plot for single sample
"""
""" schema_exposures_single_sample = {
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
  return response_json(app, output) """


"""
Signature Genome Bins plot (Manhattan plot with bins for signature exposures)
"""
""" schema_signature_genome_bins = {
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
  return response_json(app, output) """


"""
Signature Genome Bins plot for single sample
"""
""" schema_signature_genome_bins_single = {
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
  return response_json(app, output) """


"""
Kataegis plot, indicators of kataegis across genome for multiple samples
"""
""" schema_kataegis = {
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
  return response_json(app, output) """


"""
Rainfall plot
"""
""" schema_rainfall = {
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
  return response_csv(app, output) """


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
Genome Event Tracks
"""
""" schema_genome_event_tracks = {
  "type": "object",
  "properties": {
    "gene_id": {"type": "string"},
    "projects": projects_schema
  }
}
@app.route('/genome-event-track', methods=['POST'])
def route_genome_event_track():
  req = request.get_json(force=True)
  validate(req, schema_genome_event_tracks)

  output = plot_genome_event_track(req["gene_id"], req["projects"])
  return response_json(app, output) """


"""
Autocomplete gene ID
"""
""" schema_autocomplete_gene = {
  "type": "object",
  "properties": {
    "gene_id_partial": {"type": "string"}
  }
}
@app.route('/autocomplete-gene', methods=['POST'])
def route_autocomplete_gene():
  req = request.get_json(force=True)
  validate(req, schema_autocomplete_gene)

  output = autocomplete_gene(req["gene_id_partial"])
  return response_json(app, output)
 """

"""
Karyotype
"""
""" @app.route('/karyotype', methods=['POST'])
def route_karyotype():
  output = plot_karyotypes()
  return response_csv(app, output)
 """

"""
Samples listing
"""
schema_samples = {
  "type": "object",
  "properties": {
    "projects": projects_schema
  }
}
@app.route('/scale-samples', methods=['POST'])
def route_scale_samples():
  req = request.get_json(force=True)
  validate(req, schema_samples)

  output = scale_samples(req["projects"])
  if len(output) != len(set(output)):
    print("WARNING: Duplicate sample IDs")
  return response_json(app, output)


if __name__ == '__main__':
  app.run(
      host='0.0.0.0',
      debug=bool(os.environ.get('DEBUG', '')), 
      port=int(os.environ.get('PORT', 8000)),
      use_reloader=True
  )
