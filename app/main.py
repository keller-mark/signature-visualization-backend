from flask import Flask, request
from plot_processing import PlotProcessing

from web_constants import *
from validation_utils import *
from response_utils import *

app = Flask(__name__)

@app.route('/signature-genome-bins', methods=['POST'])
def route_signature_genome_bins():
  req = request.get_json(force=True)
  region_width = int(json_or(req, 'regionWidth', 1000000, r'^\d+$'))
  signatures = json_or(req, 'signatures', [], r'.*')
  projects = json_or(req, 'sources', [], PROJ_RE)

  output = PlotProcessing.signature_genome_bins(region_width, signatures, projects)
  return response_json(app, output)

@app.route('/signature-genome-bins-single-donor', methods=['POST'])
def route_signature_genome_bins_single():
  req = request.get_json(force=True)
  region_width = int(json_or(req, 'regionWidth', 1000000, r'^\d+$'))
  signatures = json_or(req, 'signatures', [], r'.*')
  proj_id = json_or(req, 'proj_id', "", PROJ_RE)
  donor_id = json_or(req, 'donor_id', "")

  output = PlotProcessing.signature_genome_bins(region_width, signatures, [proj_id], single_donor_id=donor_id)
  return response_json(app, output)

@app.route('/kataegis', methods=['POST'])
def route_kataegis():
  req = request.get_json(force=True)
  projects = json_or(req, 'sources', [], PROJ_RE)

  output = PlotProcessing.kataegis(projects)
  return response_json(app, output)

@app.route('/kataegis-rainfall', methods=['POST'])
def route_kataegis_rainfall():
  req = request.get_json(force=True)
  proj_id = json_or(req, 'proj_id', "", PROJ_RE)
  donor_id = json_or(req, 'donor_id', "")

  output = PlotProcessing.kataegis_rainfall(proj_id, donor_id)
  return response_csv(app, output)

@app.route('/exposures', methods=['POST'])
def route_exposures():
  req = request.get_json(force=True)
  signatures = json_or(req, 'signatures', [], r'.*')
  projects = json_or(req, 'sources', [], PROJ_RE)

  output = PlotProcessing.signature_exposures(signatures, projects)

  return response_json(app, output)

@app.route('/exposures-single-donor', methods=['POST'])
def route_exposures_single():
  req = request.get_json(force=True)
  signatures = json_or(req, 'signatures', [], r'.*')
  proj_id = json_or(req, 'proj_id', "", PROJ_RE)
  donor_id = json_or(req, 'donor_id', "")

  output = PlotProcessing.signature_exposures(signatures, [proj_id], single_donor_id=donor_id)

  return response_json(app, output)

@app.route('/signature', methods=['POST'])
def route_signature():
  req = request.get_json(force=True)
  signature = json_or(req, 'signature', "", r'.*')
  output = PlotProcessing.signature(name=signature)
  return response_json(app, output)

@app.route('/data-listing', methods=['POST'])
def route_data_listing():
  output = PlotProcessing.data_listing_json()
  return response_json(app, output)

@app.route('/chromosomes', methods=['POST'])
def route_chromosomes():
  output = CHROMOSOMES
  return response_json(app, output)

@app.route('/karyotype', methods=['POST'])
def route_karyotype():
  output = PlotProcessing.chromosome_bands()
  return response_csv(app, output)

@app.route('/samples-with-signatures', methods=['POST'])
def route_samples_with_signatures():
  req = request.get_json(force=True)
  signatures = json_or(req, 'signatures', [], r'.*')
  projects = json_or(req, 'sources', [], PROJ_RE)

  output = PlotProcessing.samples_with_signatures(signatures, projects)

  return response_json(app, output)

@app.route('/clustering', methods=['POST'])
def route_clustering():
  req = request.get_json(force=True)
  signatures = json_or(req, 'signatures', [], r'.*')
  projects = json_or(req, 'sources', [], PROJ_RE)

  output = PlotProcessing.clustering(signatures, projects)

  return response_json(app, output)

if __name__ == '__main__':
  app.run(
      host='0.0.0.0',
      debug=bool(os.environ.get('DEBUG', '')), 
      port=int(os.environ.get('PORT', 8000)),
      use_reloader=True
  )
