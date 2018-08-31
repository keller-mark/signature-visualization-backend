import pandas as pd
import numpy as np
from web_constants import *
from plot_processing import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData


def plot_signature_exposures(chosen_sigs_by_mut_type, projects, single_sample_id=None):
    signatures_by_mut_type = get_signatures_by_mut_type(chosen_sigs_by_mut_type)
    result = []

    if single_sample_id != None: # single donor request
      assert(len(projects) == 1)
    
    project_metadata = PlotProcessing.project_metadata()
    for proj_id in projects:
        proj = ProjectData(proj_id)
        clinical_df = proj.get_clinical_df()
        samples_df = proj.get_samples_df()
        samples = samples_df[SAMPLE].tolist()

        clinical_dict = clinical_df.to_dict(orient='index')

        exps_by_mut_type = dict()

        for mut_type in SIG_TYPES.keys():
            signatures = signatures_by_mut_type[mut_type]
            counts_df = proj.get_counts_df(mut_type)

            if single_sample_id != None: # single donor request
                counts_df = counts_df.loc[[single_sample_id], :]
            
            if len(counts_df) > 0:
                # compute exposures
                exps_df = signatures.get_exposures(counts_df)
                # multiply exposures by total mutations for each donor
                exps_df = exps_df.apply(lambda row: row * counts_df.loc[row.name, :].sum(), axis=1)

                # convert dfs to single array
                exps_by_mut_type[mut_type] = exps_df.to_dict(orient='index')
        
        def create_sample_obj(sample_id):
            return {
                "sample_id": sample_id,
                "proj_id": proj_id,
                "exposures": dict([ (mut_type, exps_by_mut_type[mut_type][sample_id]) for mut_type in SIG_TYPES.keys()]),
                "clinical": clinical_dict[sample_id]
            }
            proj_result = list(map(create_sample_obj, samples))
            # concatenate project array into result array
            result = (result + proj_result)
    return result