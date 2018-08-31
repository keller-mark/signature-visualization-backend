import os
from yaml import load
from yaml import Loader
from web_constants import *
from signatures import Signatures
from project_data import ProjectData, get_all_project_data_as_json


def get_signatures_per_cancer_type():
    if not os.path.isfile(SIGS_PER_CANCER_TYPE_FILE):
      return None
    with open(SIGS_PER_CANCER_TYPE_FILE) as data_file:  
      active_sigs = load(data_file, Loader=Loader)
    return active_sigs


def plot_data_listing():
    # instantiate a signatures object for each signature type
    signature_types = [Signatures(sig_type) for sig_type in SIG_TYPES.values()]
    return {
      "projects": get_all_project_data_as_json(),
      "sigs": dict([(st.get_type(), st.get_metadata()) for st in signature_types]),
      "sig_per_cancer_type": get_signatures_per_cancer_type()
    }