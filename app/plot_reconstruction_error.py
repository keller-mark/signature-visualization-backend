import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data


def plot_reconstruction_error(chosen_sigs, projects, mut_type, single_sample_id=None, exp_normalize=False):
    result = []

    signatures = get_signatures_by_mut_type({mut_type: chosen_sigs})[mut_type]

    if single_sample_id != None: # single sample request
      assert(len(projects) == 1)
    
    project_data = get_selected_project_data(projects)
    for proj in project_data:
        proj_id = proj.get_proj_id()

        if single_sample_id != None: # single sample request
            samples = [single_sample_id]
        else:
            samples = proj.get_samples_list()
        
        counts_df = pd.DataFrame(index=samples, columns=[])
        # Join counts df with sample df, then fill with zeros
        counts_df = counts_df.join(proj.get_counts_df(mut_type), how='outer')
        counts_df = counts_df.fillna(value=0)
        
        if single_sample_id != None: # single sample request
            try:
                counts_df = counts_df.loc[[single_sample_id], :]
            except KeyError:
                counts_df = counts_df.drop(counts_df.index)
                continue

        if counts_df.max().max() == 0:
            continue

        if counts_df.shape[0] > 0 and len(signatures.get_chosen_names()) > 0:
            # compute exposures
            exps_df = signatures.get_exposures(counts_df)
            exps_df = exps_df.fillna(value=0)
            # multiply exposures by total mutations for each donor
            if not exp_normalize:
                counts_totals_series = counts_df.sum(axis='columns')
                exps_df = exps_df.apply(lambda row: row * counts_totals_series[row.name], axis=1)
                exps_totals_series = exps_df.sum(axis='columns')
                exps_df["error"] = counts_totals_series - exps_totals_series
            else:
                exps_totals_series = exps_df.sum(axis='columns')
                exps_df["error"] = 1.0 - exps_totals_series

            proj_result = exps_df[["error"]].to_dict(orient='index')

            def create_sample_obj(sample_id):
                sample_obj = proj_result[sample_id]
                sample_obj["sample_id"] = sample_id
                return sample_obj
            proj_result = list(map(create_sample_obj, samples))
            # concatenate project array into result array
            result = (result + proj_result)
    
    if single_sample_id != None: # single sample request
        result = result[0]

    return result