import pandas as pd
import numpy as np
from web_constants import *
from plot_processing import *
from signatures import Signatures


def plot_signature_exposures(sigs, projects, single_donor_id=None):
    signatures = Signatures(SIGS_FILE, SIGS_META_FILE, chosen_sigs=sigs)
    sig_names = signatures.get_chosen_names()
    result = []

    if single_donor_id != None: # single donor request
      assert(len(projects) == 1)
    
    project_metadata = PlotProcessing.project_metadata()
    for proj_id in projects:
        if project_metadata[proj_id][HAS_COUNTS]:
            # counts data
            counts_filepath = project_metadata[proj_id]["counts_sbs_path"]
            counts_df = PlotProcessing.pd_fetch_tsv(counts_filepath, index_col=0)
            if single_donor_id != None: # single donor request
                counts_df = counts_df.loc[[single_donor_id], :]
            counts_df = counts_df.dropna(how='any', axis='index')
            donors = list(counts_df.index.values)
            # clinical data
            clinical_df = pd.DataFrame([], columns=[], index=donors)
            if project_metadata[proj_id][HAS_CLINICAL]:
                donor_filepath = project_metadata[proj_id]["clinical_path"]
                temp_clinical_df = PlotProcessing.pd_fetch_tsv(donor_filepath, index_col=0)
                clinical_df = clinical_df.join(temp_clinical_df, how='left')
            clinical_df = clinical_df.fillna(value='nan')
            
            if len(counts_df) > 0:
                # compute exposures
                exps_df = signatures.get_exposures(counts_df)
                # multiply exposures by total mutations for each donor
                exps_df = exps_df.apply(lambda row: row * counts_df.loc[row.name, :].sum(), axis=1)

                # convert dfs to single array
                exps_dict = exps_df.to_dict(orient='index')
                clinical_dict = clinical_df.to_dict(orient='index')
                def create_donor_obj(donor_id):
                    return {
                        "donor_id": donor_id,
                        "proj_id": proj_id,
                        "exposures": exps_dict[donor_id],
                        "clinical": clinical_dict[donor_id]
                    }
                proj_result = list(map(create_donor_obj, donors))
                # concatenate project array into result array
                result = (result + proj_result)
    return result