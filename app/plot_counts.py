import pandas as pd
import numpy as np

from web_constants import *
from compute_counts import compute_counts

def plot_counts(chosen_sigs, projects, mut_type, single_sample_id=None, normalize=False):
    result = []

    counts_df = compute_counts(chosen_sigs, projects, mut_type, single_sample_id=single_sample_id, normalize=normalize)

    counts_df.index = counts_df.index.rename("sample_id")
    counts_df = counts_df.reset_index()
    result = counts_df.to_dict('records')
    
    return result