import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

from compute_reconstruction import compute_reconstruction
from compute_counts import compute_counts
from scale_samples import scale_samples

def scale_reconstruction(chosen_sigs, projects, mut_type, single_sample_id=None, normalize=False, tricounts_method=None):

    reconstruction_df = compute_reconstruction(chosen_sigs, projects, mut_type, single_sample_id=single_sample_id, normalize=normalize, tricounts_method=tricounts_method)
    reconstruction_max = reconstruction_df.max().max()

    counts_df = compute_counts(chosen_sigs, projects, mut_type, single_sample_id=single_sample_id, normalize=normalize)
    counts_max = counts_df.max().max()

    return [0, max(reconstruction_max, counts_max)]