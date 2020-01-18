import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data


def compute_counts(chosen_sigs, projects, mut_type, single_sample_id=None, normalize=False):

    signatures = get_signatures_by_mut_type({mut_type: chosen_sigs})[mut_type]
    project_data = get_selected_project_data(projects)

    counts_df = pd.DataFrame(index=[], data=[], columns=signatures.get_contexts())

    for proj in project_data:
        proj_id = proj.get_proj_id()
        samples = proj.get_samples_list()

        if single_sample_id != None:
            if single_sample_id in samples:
                samples = [single_sample_id]
            else:
                continue
        
        proj_counts_df = pd.DataFrame(index=samples, columns=[])
        proj_counts_df = proj_counts_df.join(proj.get_counts_df(mut_type), how='outer')
        proj_counts_df = proj_counts_df.fillna(value=0)
        proj_counts_df = proj_counts_df[signatures.get_contexts()]

        if single_sample_id != None and single_sample_id in samples:
            proj_counts_df = proj_counts_df.loc[[single_sample_id]]

        counts_df = counts_df.append(proj_counts_df)
        
    if normalize:
        counts_totals_series = counts_df.sum(axis='columns')
        counts_df = counts_df.divide(counts_totals_series, axis='index')

    return counts_df[signatures.get_contexts()]