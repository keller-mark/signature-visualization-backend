import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

from compute_exposures import compute_exposures

def scale_exposures(chosen_sigs, projects, mut_type, single_sample_id=None, exp_sum=False, exp_normalize=False, tricounts_method=None):
    result = [0, 0]

    exps_df = compute_exposures(chosen_sigs, projects, mut_type, single_sample_id=single_sample_id, normalize=exp_normalize, tricounts_method=tricounts_method)
                
    if exp_sum:
        exps_df = exps_df.sum(axis=1)
        exps_df_max = exps_df.max()
    else:
        exps_df_max = exps_df.max().max()
    
    exps_df_max = exps_df_max if pd.notnull(exps_df_max) else 0.0

    result = [0, exps_df_max]
    return result