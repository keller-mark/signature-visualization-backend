import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

from compute_counts import compute_counts

def compute_exposures(chosen_sigs, projects, mut_type, single_sample_id=None, normalize=False):

    signatures = get_signatures_by_mut_type({mut_type: chosen_sigs})[mut_type]
    project_data = get_selected_project_data(projects)

    counts_df = compute_counts(chosen_sigs, projects, mut_type, single_sample_id=single_sample_id, normalize=False)
    
    exps_df = pd.DataFrame(index=[], data=[], columns=signatures.get_chosen_names())

    if counts_df.shape[0] > 0 and len(signatures.get_chosen_names()) > 0:
        # compute exposures
        exps_df = signatures.get_exposures(counts_df)
        exps_df = exps_df.fillna(value=0)
        # multiply exposures by total mutations for each sample
        if not normalize:
            exps_df = exps_df.apply(lambda row: row * counts_df.loc[row.name, :].sum(), axis=1)
    
    exps_df = exps_df.fillna(value=0)
    
    return exps_df