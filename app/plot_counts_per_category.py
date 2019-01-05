import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data


def plot_counts_per_category(chosen_sigs, projects, mut_type, single_sample_id=None, exp_normalize=False):
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

        if counts_df.shape[0] > 0 and len(signatures.get_chosen_names()) > 0:
            
            counts_totals_series = counts_df.sum(axis='columns')
            if exp_normalize:
                counts_df = counts_df.divide(counts_totals_series, axis='index')

            proj_result = counts_df.to_dict(orient='index')

            def create_sample_obj(sample_id):
                sample_obj = proj_result[sample_id]
                sample_obj["sample_id"] = sample_id
                return sample_obj

            proj_result = list(map(create_sample_obj, samples))
            # concatenate project array into result array
            result = (result + proj_result)
    
    if single_sample_id != None: # single sample request
        result_obj = result[0]
        result = []
        for cat, value in result_obj.items():
            result.append({
                "cat_" + mut_type: cat,
                "count_" + mut_type + "_" + single_sample_id: value
            })

    return result