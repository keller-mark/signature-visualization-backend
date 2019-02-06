import os
from web_constants import *
from signatures import Signatures
from project_data import ProjectData, get_all_project_data_as_json, get_all_tissue_types_as_json
from sig_data import SigData, get_all_sig_data_as_json, get_all_cancer_type_mappings_as_json
from tricounts_data import get_tricounts_methods

def plot_data_listing():
    return {
      "projects": get_all_project_data_as_json(),
      "signatures": get_all_sig_data_as_json(),
      "cancer_type_map": get_all_cancer_type_mappings_as_json(),
      "tissue_types": get_all_tissue_types_as_json(),
      "tricounts_methods": get_tricounts_methods()
    }