import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures
from project_data import ProjectData, get_selected_project_data


def plot_exposures(chosen_sigs, projects, mut_type, single_sample_id=None, exp_normalize=False):
    result = []

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

        # TODO: join counts df with sample df, then fill with zeros

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
            if not exp_normalize:
                exps_df = exps_df.apply(lambda row: row * counts_df.loc[row.name, :].sum(), axis=1)
            # convert dfs to single array
            proj_result = exps_df.to_dict(orient='index')

            def create_sample_obj(sample_id):
                sample_obj = proj_result[sample_id]
                sample_obj["sample_id"] = sample_id
                return sample_obj
            proj_result = list(map(create_sample_obj, samples))
            # concatenate project array into result array
            result = (result + proj_result)

    return result