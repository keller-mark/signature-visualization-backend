import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

from compute_counts import compute_counts

def scale_counts_per_category(chosen_sigs, projects, mut_type, single_sample_id=None, normalize=False):

    counts_df = compute_counts(chosen_sigs, projects, mut_type, single_sample_id=single_sample_id, normalize=normalize)
    counts_max = counts_df.max().max()

    return [0, counts_max]