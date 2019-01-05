import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

from compute_exposures import compute_exposures
from scale_samples import scale_samples

def plot_exposures(chosen_sigs, projects, mut_type, single_sample_id=None, normalize=False):
    result = []

    exps_df = compute_exposures(chosen_sigs, projects, mut_type, single_sample_id=single_sample_id, normalize=normalize)
    
    if single_sample_id == None:
        samples = scale_samples(projects)
    else:
        samples = [single_sample_id]

    exps_dict = exps_df.to_dict(orient='index')

    def create_sample_obj(sample_id):
        sample_obj = exps_dict[sample_id]
        sample_obj["sample_id"] = sample_id
        return sample_obj
    
    result = list(map(create_sample_obj, samples))

    if single_sample_id != None:
        result = result[0]
        for sig, value in result_obj.items():
            result.append({
                "sig_" + mut_type + "_" + single_sample_id: sig,
                "exp_" + mut_type + "_" + single_sample_id: value
            })

    return result