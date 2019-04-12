import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

from compute_counts import compute_counts
from compute_exposures import compute_exposures

def compute_reconstruction(chosen_sigs, projects, mut_type, single_sample_id=None, normalize=False, tricounts_method=None):
    
    signatures = get_signatures_by_mut_type({mut_type: chosen_sigs}, tricounts_method=tricounts_method)[mut_type]

    counts_df = compute_counts(chosen_sigs, projects, mut_type, single_sample_id=single_sample_id, normalize=normalize)
    exps_df = compute_exposures(chosen_sigs, projects, mut_type, single_sample_id=single_sample_id, normalize=normalize, tricounts_method=tricounts_method)

    reconstruction_array = np.dot(exps_df.values, signatures.get_2d_array())
    reconstruction_df = pd.DataFrame(index=list(counts_df.index.values), columns=signatures.get_contexts(), data=reconstruction_array)
    reconstruction_df = reconstruction_df[list(counts_df.columns.values)]
    
    return reconstruction_df