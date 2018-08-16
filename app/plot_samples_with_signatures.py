import pandas as pd
import numpy as np
from web_constants import *
from plot_processing import *
from signatures import Signatures

def plot_samples_with_signatures(sigs, projects):
    signatures = Signatures(SIGS_FILE, SIGS_META_FILE, chosen_sigs=sigs)
    sig_names = signatures.get_chosen_names()
    
    # array containing an object for each signature
    # example: { signatures: {"SBS 1": {"proj_id": number, ...}, ...}, "projects": { "proj_id": num_samples}, ... }
    result = {
      "signatures": {},
      "projects": {}
    }

    project_metadata = PlotProcessing.project_metadata()
    for proj_id in projects:
        if project_metadata[proj_id][HAS_COUNTS]:
            # counts data
            counts_filepath = project_metadata[proj_id]["counts_sbs_path"]
            counts_df = PlotProcessing.pd_fetch_tsv(counts_filepath, index_col=0)
            counts_df = counts_df.dropna(how='any', axis='index')
            result["projects"][proj_id] = len(counts_df.index.values)
            
            if len(counts_df) > 0:
                # compute exposures
                exps_df = signatures.get_exposures(counts_df)
                # multiply exposures by total mutations for each donor
                exps_df = exps_df.apply(lambda row: row * counts_df.loc[row.name, :].sum(), axis=1)
                # for each signature, get number of samples with at least one mutation attributed
                samples_with_sig = exps_df.apply(lambda col: col.loc[col >= 1].size, axis='index')
                
                for sig_name, num_samples in samples_with_sig.to_dict().items():
                    try:
                        result["signatures"][sig_name][proj_id] = num_samples
                    except KeyError:
                        result["signatures"][sig_name] = { proj_id: num_samples }
    return result