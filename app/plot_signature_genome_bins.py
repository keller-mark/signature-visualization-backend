import pandas as pd
import numpy as np
from web_constants import *
from signatures import Signatures
from plot_processing import *

dtype = {
    SAMPLE: str,
    POS_START: int,
    CAT_SBS_96: str,
    CHR: str
}

def plot_signature_genome_bins(region_width, sigs, projects, single_donor_id=None):
    signatures = Signatures(SIGS_FILE, SIGS_META_FILE, chosen_sigs=sigs)
    # validation
    if region_width < 10000: # will be too slow, stop processing
        return None

    if single_donor_id != None: # single donor request
        assert(len(projects) == 1)
    
    sig_names = signatures.get_chosen_names()
    chr_dfs = {}
    for chr_name, chr_len in CHROMOSOMES.items():
        chr_regions = list(range(0, chr_len, region_width))
        # each chr_df: sigs x regions
        chr_dfs[chr_name] = pd.DataFrame(index=sig_names, columns=chr_regions)

    project_metadata = PlotProcessing.project_metadata()
    for proj_id in projects:
        # load data for project
        if project_metadata[proj_id][HAS_SSM] and project_metadata[proj_id][HAS_COUNTS]:
            ssm_filepath = project_metadata[proj_id]["extended_sbs_path"]
            counts_filepath = project_metadata[proj_id]["counts_sbs_path"]
            
            ssm_df = PlotProcessing.pd_fetch_tsv(ssm_filepath, dtype=dtype, usecols=dtype.keys())
            counts_df = PlotProcessing.pd_fetch_tsv(counts_filepath, index_col=0)
            counts_df = counts_df.dropna(axis=0, how='any')
            
            if single_donor_id != None: # single donor request
                counts_df = counts_df.loc[[single_donor_id], :]
                ssm_df = ssm_df.loc[ssm_df[SAMPLE] == single_donor_id]

            if len(counts_df) > 0:
                # compute exposures
                exps_df = signatures.get_exposures(counts_df)
                assignments_df = signatures.get_assignments(exps_df)
                # set region of genome
                ssm_df['region'] = ssm_df.apply(lambda row: row[POS_START] // region_width * region_width, axis=1)
                # add signature column. TODO: figure out why this step takes so long
                ssm_df['signature'] = ssm_df.apply(lambda row: assignments_df.loc[row[SAMPLE], row[CAT_SBS_96]] if pd.notnull(row[CAT_SBS_96]) else None, axis=1)
                # for each chromosome
                for chr_name, ssm_chr_df in ssm_df.groupby([CHR]):
                    # aggregate
                    groups = ssm_chr_df.groupby(['region', 'signature'])
                    counts = groups.size().reset_index(name='counts')   
                    regions_df = counts.pivot(index='signature', columns='region', values='counts')
                    # sum
                    chr_dfs[str(chr_name)] = chr_dfs[str(chr_name)].add(regions_df, fill_value=0)
        
    # finalize
    for chr_name in CHROMOSOMES.keys():
        chr_dfs[chr_name].fillna(value=0, inplace=True)
        chr_dfs[chr_name][list(chr_dfs[chr_name].columns.values)] = chr_dfs[chr_name][list(chr_dfs[chr_name].columns.values)].astype(int)
        chr_dfs[chr_name] = chr_dfs[chr_name].transpose().to_dict(orient='index')
    return chr_dfs