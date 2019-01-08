import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

from compute_counts import compute_counts
from compute_reconstruction import compute_reconstruction

def compute_reconstruction_error(chosen_sigs, projects, mut_type, single_sample_id=None, normalize=False):
    
    counts_df = compute_counts(chosen_sigs, projects, mut_type, single_sample_id=single_sample_id, normalize=normalize)
    reconstruction_df = compute_reconstruction(chosen_sigs, projects, mut_type, single_sample_id=single_sample_id, normalize=normalize)
    
    reconstruction_df = reconstruction_df.subtract(counts_df, axis='index')
    return reconstruction_df