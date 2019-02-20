import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

from compute_reconstruction_error import compute_reconstruction_error
from scale_samples import scale_samples

def scale_reconstruction_error(chosen_sigs, projects, mut_type, single_sample_id=None, normalize=False, tricounts_method=None):

    reconstruction_error_df = compute_reconstruction_error(chosen_sigs, projects, mut_type, single_sample_id=single_sample_id, normalize=normalize, tricounts_method=tricounts_method)
    reconstruction_error_min = reconstruction_error_df.min().min()
    reconstruction_error_max = reconstruction_error_df.max().max()

    return [reconstruction_error_min, reconstruction_error_max]