import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

from compute_counts import compute_counts

def compute_exposures(chosen_sigs, projects, mut_type, single_sample_id=None, normalize=False, tricounts_method=None):

    signatures = get_signatures_by_mut_type({mut_type: chosen_sigs}, tricounts_method=None)[mut_type]
    project_data = get_selected_project_data(projects)

    exps_df = pd.DataFrame(index=[], data=[], columns=signatures.get_chosen_names())

    for proj in project_data:
        # Check if need to get signatures based on each project's sequencing type before computing exposures
        if tricounts_method == "By Study":
            # Note that the tricounts_method variable here represents a boolean value, but the one we are passing in to `get_signatures_by_mut_type` represents a sequencing type. 
            # TODO: change variable names to make this obvious
            proj_signatures = get_signatures_by_mut_type({mut_type: chosen_sigs}, tricounts_method=proj.get_seq_type())[mut_type]
        else:
            proj_signatures = signatures
        proj_counts_df = compute_counts(chosen_sigs, [proj.get_proj_id()], mut_type, single_sample_id=single_sample_id, normalize=False)

        if proj_counts_df.shape[0] > 0 and len(proj_signatures.get_chosen_names()) > 0:
            # compute exposures
            proj_exps_df = proj_signatures.get_exposures(proj_counts_df)
            proj_exps_df = proj_exps_df.fillna(value=0)
            # multiply exposures by total mutations for each sample
            if not normalize:
                proj_exps_df = proj_exps_df.apply(lambda row: row * proj_counts_df.loc[row.name, :].sum(), axis=1)
        
            exps_df = exps_df.append(proj_exps_df)
    
    exps_df = exps_df.fillna(value=0)
    
    return exps_df