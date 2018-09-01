import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

def plot_samples_with_signatures(chosen_sigs_by_mut_type, projects):
    signatures_by_mut_type = get_signatures_by_mut_type(chosen_sigs_by_mut_type)

    # array containing an object for each signature
    # example: { signatures: {"SBS 1": {"proj_id": number, ...}, ...}, "projects": { "proj_id": num_samples}, ... }
    result = {
      "signatures": dict([(mut_type, {}) for mut_type in MUT_TYPES]),
      "projects": {}
    }

    project_data = get_selected_project_data(projects)
    for proj in project_data:
        proj_id = proj.get_proj_id()

        num_samples = len(proj.get_samples_list())
        result["projects"][proj_id] = num_samples

        for mut_type in MUT_TYPES:
            signatures = signatures_by_mut_type[mut_type]

            # counts data
            counts_df = proj.get_counts_df(mut_type)
            
            if len(counts_df) > 0:
                # compute exposures
                exps_df = signatures.get_exposures(counts_df)
                # multiply exposures by total mutations for each donor
                exps_df = exps_df.apply(lambda row: row * counts_df.loc[row.name, :].sum(), axis=1)
                # for each signature, get number of samples with at least one mutation attributed
                samples_with_sig = exps_df.apply(lambda col: col.loc[col >= 1].size, axis='index')
                
                for sig_name, num_samples in samples_with_sig.to_dict().items():
                    try:
                        result["signatures"][mut_type][sig_name][proj_id] = num_samples
                    except KeyError:
                        result["signatures"][mut_type][sig_name] = { proj_id: num_samples }
    return result