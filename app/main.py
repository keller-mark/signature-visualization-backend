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
  signatures = json_or(req, 'signatures', ["COSMIC 1"], r'.*')
  projects = json_or(req, 'sources', ["PCAWG-BRCA-EU", "PCAWG-LIHC-US"], PROJ_RE)

  output = PlotProcessing.muts_by_sig_points(region_width, signatures, projects)

  return response_json(app, output)

@app.route('/kataegis', methods=['POST'])
def route_kataegis():
  req = request.get_json(force=True)
  projects = json_or(req, 'sources', ["PCAWG-BRCA-EU", "PCAWG-LIHC-US"], PROJ_RE)

  output = PlotProcessing.kataegis(projects)
  return response_json(app, output)

@app.route('/kataegis-rainfall', methods=['POST'])
def route_kataegis_rainfall():
  req = request.get_json(force=True)
  proj_id = json_or(req, 'proj_id', "PCAWG-PRAD-UK", PROJ_RE)
  donor_id = json_or(req, 'donor_id', "DO51965")

  output = PlotProcessing.kataegis_rainfall(proj_id, donor_id)
  return response_csv(app, output)

@app.route('/exposures', methods=['POST'])
def route_exposures():
  req = request.get_json(force=True)
  signatures = json_or(req, 'signatures', ["COSMIC 1", "COSMIC 2"], r'.*')
  projects = json_or(req, 'sources', ["PCAWG-BRCA-EU", "PCAWG-LIHC-US"], PROJ_RE)

  output = PlotProcessing.signature_exposures(signatures, projects)

  return response_csv(app, output)

@app.route('/signatures', methods=['POST'])
def route_signatures():  
  output = PlotProcessing.sigs()
  return response_csv(app, output)

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

if __name__ == '__main__':
  app.run(
      host='0.0.0.0',
      debug=bool(os.environ.get('DEBUG', '')), 
      port=int(os.environ.get('PORT', 8000)),
      use_reloader=True
  )
