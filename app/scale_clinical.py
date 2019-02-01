import pandas as pd
import numpy as np
import pickle

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

from plot_clinical import plot_clinical, plot_clinical_variables, meta_clinical_df

def scale_clinical(projects):
    result = {}
    clinical_df = plot_clinical(projects)
    for clinical_var in plot_clinical_variables():

        clinical_vals = list(set(list(clinical_df[clinical_var].unique())) - set(['nan']))
        clinical_vals = sorted(clinical_vals)
    return result


