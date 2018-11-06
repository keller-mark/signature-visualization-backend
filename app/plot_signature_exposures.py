import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data


def plot_signature_exposures(chosen_sigs_by_mut_type, projects, single_sample_id=None):
    signatures_by_mut_type = get_signatures_by_mut_type(chosen_sigs_by_mut_type)
    result = []

    if single_sample_id != None: # single sample request
      assert(len(projects) == 1)
    
    project_data = get_selected_project_data(projects)
    for proj in project_data:
        proj_id = proj.get_proj_id()
        clinical_df = proj.get_clinical_df()

        if single_sample_id != None: # single sample request
            samples = [single_sample_id]
        else:
            samples = proj.get_samples_list()

        clinical_dict = clinical_df.to_dict(orient='index')

        exps_by_mut_type = {}

        for mut_type in MUT_TYPES:
            signatures = signatures_by_mut_type[mut_type]
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
                # convert dfs to single array
                exps_by_mut_type[mut_type] = exps_df.to_dict(orient='index')
        
        def lookup_sample(sample_id, mut_type):
            try:
                return exps_by_mut_type[mut_type][sample_id]
            except KeyError:
                return {}
        
        def create_sample_obj(sample_id):
            return {
                "sample_id": sample_id,
                "proj_id": proj_id,
                "exposures": dict([ (mut_type, lookup_sample(sample_id, mut_type)) for mut_type in MUT_TYPES]),
                "clinical": clinical_dict[sample_id]
            }
        proj_result = list(map(create_sample_obj, samples))
        # concatenate project array into result array
        result = (result + proj_result)
    return result