import pandas as pd
import numpy as np

from scipy.spatial import distance

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

from compute_counts import compute_counts
from compute_reconstruction import compute_reconstruction
from scale_samples import scale_samples

def plot_reconstruction_cosine_similarity(chosen_sigs, projects, mut_type, single_sample_id=None):
    result = []

    reconstruction_df = compute_reconstruction(chosen_sigs, projects, mut_type, single_sample_id=single_sample_id, normalize=False)
    counts_df = compute_counts(chosen_sigs, projects, mut_type, single_sample_id=single_sample_id, normalize=False)

    if single_sample_id == None:
        samples = scale_samples(projects)
    else:
        samples = [single_sample_id]

    def create_sample_obj(sample_id):
        sample_obj = {}
        cosine_similarity = 1.0 - distance.cosine(reconstruction_df.loc[sample_id, :].values, counts_df.loc[sample_id, :].values)
        sample_obj["cosine_similarity_" + mut_type] = cosine_similarity if pd.notnull(cosine_similarity) else 0.0
        sample_obj["sample_id"] = sample_id
        return sample_obj

    result = list(map(create_sample_obj, samples))
        
    if single_sample_id != None: # single sample request
        result = result[0]

    return result