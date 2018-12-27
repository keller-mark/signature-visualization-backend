import os
from yaml import load
from yaml import Loader
from web_constants import *
from signatures import Signatures
from project_data import ProjectData, get_all_project_data_as_json
from sig_data import SigData, get_all_sig_data_as_json

def plot_data_listing():
    return {
      "projects": get_all_project_data_as_json(),
      "signatures": get_all_sig_data_as_json()
    }