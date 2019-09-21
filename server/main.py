from starlette.applications import Starlette
import uvicorn
import os

from jsonschema import validate
from response_utils import *
from web_constants import *

from plot_data_listing import plot_data_listing

from plot_clustering import plot_clustering

from scale_samples import scale_samples

from plot_exposures import plot_exposures
from scale_exposures import scale_exposures

from plot_counts import plot_counts
from scale_counts import scale_counts

from plot_counts_by_category import plot_counts_by_category

from plot_samples_meta import plot_samples_meta

from plot_gene_mut_track import plot_gene_mut_track, autocomplete_gene, plot_pathways_listing
from plot_gene_exp_track import plot_gene_exp_track
from plot_gene_cna_track import plot_gene_cna_track
from plot_clinical import plot_clinical
from scale_clinical import scale_clinical
from plot_survival import plot_survival

# Reconstruction plots
from plot_counts_per_category import plot_counts_per_category
from plot_reconstruction import plot_reconstruction
from plot_reconstruction_error import plot_reconstruction_error

from scale_contexts import scale_contexts
from plot_signature import plot_signature
from plot_reconstruction_cosine_similarity import plot_reconstruction_cosine_similarity
# Sharing
from sharing_state import get_sharing_state, set_sharing_state, plot_featured_listing
from sessions import session_get, session_start, session_connect, session_post

# Authentication
from auth import NotAuthenticated, login, logout, check_token


app = Starlette(debug=bool(os.environ.get('DEBUG', '')))

""" 
Authentication helpers 
"""
@app.exception_handler(NotAuthenticated)
async def handle_not_authenticated(request, exc):
    return response_json_error(app, {"message": exc.message}, exc.status_code)

async def check_req(request, schema=None):
  req = await request.json()
  check_token(req)
  if schema != None:
    validate(req, schema)
  return req

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
async def route_data_listing(request):
  req = await check_req(request)
  output = plot_data_listing()
  return response_json(app, output)

# TODO: combine the below listing requests into the one data listing request
@app.route('/pathways-listing', methods=['POST'])
async def route_pathways_listing(request):
  req = await check_req(request)
  output = plot_pathways_listing()
  return response_json(app, output)

@app.route('/featured-listing', methods=['POST'])
async def route_featured_listing(request):
  req = await check_req(request)
  output = plot_featured_listing()
  return response_json(app, output)


"""
Signatures
"""
schema_signature = {
  "type": "object",
  "properties": {
    "signature": {"type": "string"},
    "signature_index": {"type": "string"},
    "mut_type": {"type": "string"},
    "tricounts_method": {"type": "string"}
  }
}
@app.route('/plot-signature', methods=['POST'])
async def route_plot_signature(request):
  req = await check_req(request, schema=schema_signature)

  assert(req["mut_type"] in MUT_TYPES)

  signature_index = None if req["signature_index"] == 'None' else req["signature_index"]

  output = plot_signature(req["signature"], req["mut_type"], signature_index=signature_index, tricounts_method=req["tricounts_method"])
  return response_json(app, output)

"""
Samples-by-project
"""
schema_samples_meta = {
  "type": "object",
  "properties": {
    "projects": projects_schema
  }
}
@app.route('/plot-samples-meta', methods=['POST'])
async def route_plot_samples_meta(request):
  req = await check_req(request, schema=schema_counts)

  output = plot_samples_meta(req["projects"])
  return response_json(app, output)

"""
Counts
"""
schema_counts = {
  "type": "object",
  "properties": {
    "projects": projects_schema
  }
}
@app.route('/plot-counts', methods=['POST'])
async def route_plot_counts(request):
  req = await check_req(request, schema=schema_counts)

  output = plot_counts(req["projects"])
  return response_json(app, output)

schema_counts_by_category = {
  "type": "object",
  "properties": {
    "projects": projects_schema,
    "mut_type": {"type": "string"}
  }
}
@app.route('/plot-counts-by-category', methods=['POST'])
async def route_plot_counts_by_category(request):
  req = await check_req(request, schema=schema_counts_by_category)

  output = plot_counts_by_category(req["projects"], req["mut_type"])
  return response_json(app, output)

"""
Exposures
"""
schema_exposures = {
  "type": "object",
  "properties": {
    "signatures": string_array_schema,
    "projects": projects_schema,
    "mut_type": {"type": "string"},
    "tricounts_method": {"type": "string"}
  }
}
@app.route('/plot-exposures', methods=['POST'])
async def route_plot_exposures(request):
  req = await check_req(request, schema=schema_exposures)

  assert(req["mut_type"] in MUT_TYPES)

  output = plot_exposures(req["signatures"], req["projects"], req["mut_type"], tricounts_method=req["tricounts_method"])
  return response_json(app, output)

@app.route('/plot-exposures-normalized', methods=['POST'])
async def route_plot_exposures_normalized(request):
  req = await check_req(request, schema=schema_exposures)

  assert(req["mut_type"] in MUT_TYPES)

  output = plot_exposures(req["signatures"], req["projects"], req["mut_type"], normalize=True, tricounts_method=req["tricounts_method"])
  return response_json(app, output)


@app.route('/scale-exposures-normalized', methods=['POST'])
async def route_scale_exposures_normalized(request):
  req = await check_req(request, schema=schema_exposures)

  assert(req["mut_type"] in MUT_TYPES)

  output = scale_exposures(req["signatures"], req["projects"], req["mut_type"], exp_sum=False, exp_normalize=True, tricounts_method=req["tricounts_method"])
  return response_json(app, output)

schema_exposures_single_sample = {
  "type": "object",
  "properties": {
    "signatures": string_array_schema,
    "projects": projects_schema,
    "mut_type": {"type": "string"},
    "sample_id": {"type": "string"},
    "tricounts_method": {"type": "string"}
  }
}
@app.route('/plot-exposures-single-sample', methods=['POST'])
async def route_plot_exposures_single_sample(request):
  req = await check_req(request, schema=schema_exposures_single_sample)

  assert(req["mut_type"] in MUT_TYPES)

  output = plot_exposures(req["signatures"], req["projects"], req["mut_type"], single_sample_id=req["sample_id"], normalize=False, tricounts_method=req["tricounts_method"])
  return response_json(app, output)


"""
Reconstruction error
"""
@app.route('/plot-counts-per-category-single-sample', methods=['POST'])
async def route_plot_counts_per_category_single_sample(request):
  req = await check_req(request, schema=schema_exposures_single_sample)

  assert(req["mut_type"] in MUT_TYPES)

  output = plot_counts_per_category(req["signatures"], req["projects"], req["mut_type"], single_sample_id=req["sample_id"], normalize=False)
  return response_json(app, output)

@app.route('/plot-reconstruction-single-sample', methods=['POST'])
async def route_plot_reconstruction_single_sample(request):
  req = await check_req(request, schema=schema_exposures_single_sample)

  assert(req["mut_type"] in MUT_TYPES)

  output = plot_reconstruction(req["signatures"], req["projects"], req["mut_type"], single_sample_id=req["sample_id"], normalize=False, tricounts_method=req["tricounts_method"])
  return response_json(app, output)

@app.route('/plot-reconstruction-error-single-sample', methods=['POST'])
async def route_plot_reconstruction_error_single_sample(request):
  req = await check_req(request, schema=schema_exposures_single_sample)

  assert(req["mut_type"] in MUT_TYPES)

  output = plot_reconstruction_error(req["signatures"], req["projects"], req["mut_type"], single_sample_id=req["sample_id"], normalize=False, tricounts_method=req["tricounts_method"])
  return response_json(app, output)

@app.route('/plot-reconstruction-cosine-similarity', methods=['POST'])
async def route_plot_reconstruction_cosine_similarity(request):
  req = await check_req(request, schema=schema_exposures)

  assert(req["mut_type"] in MUT_TYPES)

  output = plot_reconstruction_cosine_similarity(req["signatures"], req["projects"], req["mut_type"], tricounts_method=req["tricounts_method"])
  return response_json(app, output)

@app.route('/plot-reconstruction-cosine-similarity-single-sample', methods=['POST'])
async def route_plot_reconstruction_cosine_similarity_single_sample(request):
  req = await check_req(request, schema=schema_exposures_single_sample)

  assert(req["mut_type"] in MUT_TYPES)

  output = plot_reconstruction_cosine_similarity(req["signatures"], req["projects"], req["mut_type"], single_sample_id=req["sample_id"], tricounts_method=req["tricounts_method"])
  return response_json(app, output)




schema_contexts = {
  "type": "object",
  "properties": {
    "signatures": string_array_schema,
    "mut_type": {"type": "string"}
  }
}
@app.route('/scale-contexts', methods=['POST'])
async def route_scale_contexts(request):
  req = await check_req(request, schema=schema_contexts)

  assert(req["mut_type"] in MUT_TYPES)

  output = scale_contexts(req["signatures"], req["mut_type"])
  return response_json(app, output)


"""
Hierarchical clustering plot
"""
schema_clustering = {
  "type": "object",
  "properties": {
    "signatures": signatures_schema,
    "projects": projects_schema,
    "tricounts_method": {"type": "string"}
  }
}
@app.route('/clustering', methods=['POST'])
async def route_clustering(request):
  req = await check_req(request, schema=schema_clustering)

  output = plot_clustering(req["signatures"], req["projects"], tricounts_method=req["tricounts_method"])
  return response_json(app, output)


"""
Genome Event Tracks
"""
schema_gene_event_track = {
  "type": "object",
  "properties": {
    "gene_id": {"type": "string"},
    "projects": projects_schema
  }
}
@app.route('/plot-gene-mut-track', methods=['POST'])
async def route_gene_mut_track(request):
  req = await check_req(request, schema=schema_gene_event_track)

  output = plot_gene_mut_track(req["gene_id"], req["projects"])
  return response_json(app, output)

@app.route('/plot-gene-exp-track', methods=['POST'])
async def route_gene_exp_track(request):
  req = await check_req(request, schema=schema_gene_event_track)

  output = plot_gene_exp_track(req["gene_id"], req["projects"])
  return response_json(app, output)

@app.route('/plot-gene-cna-track', methods=['POST'])
async def route_gene_cna_track(request):
  req = await check_req(request, schema=schema_gene_event_track)

  output = plot_gene_cna_track(req["gene_id"], req["projects"])
  return response_json(app, output) 


"""
Autocomplete gene ID
"""
schema_autocomplete_gene = {
  "type": "object",
  "properties": {
    "projects": projects_schema,
    "gene_id_partial": {"type": "string"}
  }
}
@app.route('/autocomplete-gene', methods=['POST'])
async def route_autocomplete_gene(request):
  req = await check_req(request, schema=schema_autocomplete_gene)

  output = autocomplete_gene(req["gene_id_partial"], req["projects"])
  return response_json(app, output)

"""
Clinical Variable Tracks
"""
schema_clinical = {
  "type": "object",
  "properties": {
    "clinical_variable": {"type": "string"},
    "projects": projects_schema
  }
}
@app.route('/plot-clinical', methods=['POST'])
async def route_plot_clinical(request):
  req = await check_req(request, schema=schema_clinical)

  output = plot_clinical(req["projects"])
  return response_json(app, output)

@app.route('/scale-clinical', methods=['POST'])
async def route_scale_clinical(request):
  req = await check_req(request, schema=schema_clinical)

  output = scale_clinical(req["projects"])
  return response_json(app, output)

schema_survival = {
  "type": "object",
  "properties": {
    "projects": projects_schema
  }
}
@app.route('/plot-survival', methods=['POST'])
async def route_plot_survival(request):
  req = await check_req(request, schema=schema_survival)

  output = plot_survival(req["projects"])
  return response_json(app, output)

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
async def route_scale_samples(request):
  req = await check_req(request, schema=schema_samples)

  output = scale_samples(req["projects"])
  return response_json(app, output)


"""
Gene alteration scale
"""
@app.route('/scale-gene-alterations', methods=['POST'])
async def route_scale_gene_alterations(request):
  req = await check_req(request)
  output = [e.value for e in MUT_CLASS_VALS] + ["None"]
  return response_json(app, output) 

"""
Sharing: get state
"""
schema_sharing_get = {
  "type": "object",
  "properties": {
    "slug": {"type": "string"}
  }
}
@app.route('/sharing-get', methods=['POST'])
async def route_sharing_get(request):
  req = await check_req(request, schema=schema_sharing_get)
  try:
    output = get_sharing_state(req['slug'])
    return response_json(app, output)
  except:
    return response_json_error(app, {"message": "An error has occurred."}, 500)

"""
Sharing: set state
"""
schema_sharing_set = {
  "type": "object",
  "properties": {
    "state": {"type": "string"}
  }
}
@app.route('/sharing-set', methods=['POST'])
async def route_sharing_set(request):
  req = await check_req(request, schema=schema_sharing_set)
  try:
    output = set_sharing_state(req['state'])
    return response_json(app, output)
  except:
    return response_json_error(app, {"message": "An error has occurred."}, 500)

"""
Sessions
"""
schema_session_start = {
  "type": "object",
  "properties": {
    "state": {"type": "string"}
  }
}
@app.route('/session-start', methods=['POST'])
async def route_session_start(request):
  req = await check_req(request, schema=schema_session_start)
  try:
    output = session_start(req['state'])
    return response_json(app, output)
  except:
    return response_json_error(app, {"message": "An error has occurred."}, 500)

schema_session_get = {
  "type": "object",
  "properties": {
    "session_id": {"type": "string"}
  }
}
@app.route('/session-get', methods=['POST'])
async def route_session_get(request):
  req = await check_req(request, schema=schema_session_get)
  try:
    output = session_get(req['session_id'])
    return response_json(app, output)
  except:
    return response_json_error(app, {"message": "An error has occurred."}, 500)

@app.websocket_route('/session-connect')
async def route_session_connect(websocket):
  await session_connect(websocket)

schema_session_post = {
  "type": "object",
  "properties": {
    "session_id": {"type": "string"},
    "data": {"type": "object"}
  }
}
@app.route('/session-post', methods=['POST'])
async def route_session_post(request):
  req = await check_req(request, schema=schema_session_post)
  try:
    output = await session_post(req['session_id'], req['data'])
    return response_json(app, output)
  except:
    return response_json_error(app, {"message": "An error has occurred."}, 500)

""" 
Authentication routes
"""
schema_login = {
  "type": "object",
  "properties": {
    "password": {"type": "string"}
  }
}
@app.route('/login', methods=['POST'])
async def route_login(request):
  req = await request.json()
  validate(req, schema_login)
  output = login(req['password'])
  return response_json(app, output)

@app.route('/check-token', methods=['POST'])
async def route_check_token(request):
  await check_req(request)
  output = {'message': 'Authentication successful.'}
  return response_json(app, output)

@app.route('/logout', methods=['POST'])
async def route_logout(request):
  req = await check_req(request)
  logout(req['token'])
  output = {'message': 'Logout successful.'}
  return response_json(app, output)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8100)))