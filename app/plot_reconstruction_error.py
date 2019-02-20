import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

from compute_reconstruction_error import compute_reconstruction_error
from scale_samples import scale_samples

def plot_reconstruction_error(chosen_sigs, projects, mut_type, single_sample_id=None, normalize=False, tricounts_method=None):
    result = []

    reconstruction_error_df = compute_reconstruction_error(chosen_sigs, projects, mut_type, single_sample_id=single_sample_id, normalize=normalize, tricounts_method=tricounts_method)
    reconstruction_error_dict = reconstruction_error_df.to_dict(orient='index')

    if single_sample_id == None:
        samples = scale_samples(projects)
    else:
        samples = [single_sample_id]

    def create_sample_obj(sample_id):
        sample_obj = reconstruction_error_dict[sample_id]
        sample_obj["sample_id"] = sample_id
        return sample_obj

    result = list(map(create_sample_obj, samples))
    
    if single_sample_id != None: # single sample request
        result_obj = result[0]
        result = []
        for cat, value in result_obj.items():
            result.append({
                "cat_" + mut_type: cat,
                "error_" + mut_type + "_" + single_sample_id: value
            })

    return result