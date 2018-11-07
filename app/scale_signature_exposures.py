import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures
from project_data import ProjectData, get_selected_project_data


def scale_signature_exposures(chosen_sigs, projects, mut_type, single_sample_id=None):
    result = [0, 0]

    signatures = Signatures(sigs_type=SIG_TYPES[mut_type], chosen_sigs=chosen_sigs)

    if single_sample_id != None: # single sample request
      assert(len(projects) == 1)
    
    project_data = get_selected_project_data(projects)
    for proj in project_data:
        proj_id = proj.get_proj_id()

        if single_sample_id != None: # single sample request
            samples = [single_sample_id]
        else:
            samples = proj.get_samples_list()

        counts_df = proj.get_counts_df(mut_type)


        if single_sample_id != None: # single sample request
            try:
                counts_df = counts_df.loc[[single_sample_id], :]
            except KeyError:
                counts_df = counts_df.drop(counts_df.index)
                continue

        
        if counts_df.shape[0] > 0 and len(signatures.get_chosen_names()) > 0:
            # compute exposures
            exps_df = signatures.get_exposures(counts_df)
            # multiply exposures by total mutations for each donor
            exps_df = exps_df.apply(lambda row: row * counts_df.loc[row.name, :].sum(), axis=1)

            exps_df = exps_df.sum(axis=1)
            exps_df_max = exps_df.max()
            result[1] = max(result[1], exps_df_max)

    return result