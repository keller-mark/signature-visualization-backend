import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data


dtype = {
    SAMPLE: str,
    POS_START: int,
    CHR: str
}

def plot_signature_genome_bins(region_width, chosen_sigs_by_mut_type, projects, single_sample_id=None):
    signatures_by_mut_type = get_signatures_by_mut_type(chosen_sigs_by_mut_type)
    # validation
    if region_width < 10000: # will be too slow, stop processing
        return None

    if single_sample_id != None: # single sample request
        assert(len(projects) == 1)
    
    chr_dfs = {}
    for chr_name, chr_len in CHROMOSOMES.items():
        chr_dfs[chr_name] = {}
        chr_regions = list(range(0, chr_len, region_width))

        for mut_type in MUT_TYPES:
            signatures = signatures_by_mut_type[mut_type]
            sig_names = signatures.get_chosen_names()
            # each chr_df: sigs x regions
            chr_dfs[chr_name][mut_type] = pd.DataFrame(index=sig_names, columns=chr_regions)

    project_data = get_selected_project_data(projects)
    for proj in project_data:
        proj_id = proj.get_proj_id()
        
        for mut_type in MUT_TYPES:
            signatures = signatures_by_mut_type[mut_type]
            cat_colname = SIG_TYPES[mut_type]
            dtype_for_mut_type = dtype.copy()
            dtype_for_mut_type[cat_colname] = str
            ssm_df = proj.get_extended_df(mut_type, dtype=dtype_for_mut_type, usecols=dtype_for_mut_type.keys())
            counts_df = proj.get_counts_df(mut_type)

            if single_sample_id != None: # single sample request
                counts_df = counts_df.loc[[single_sample_id], :]
                ssm_df = ssm_df.loc[ssm_df[SAMPLE] == single_sample_id]

            if len(counts_df) > 0:
                # compute exposures
                exps_df = signatures.get_exposures(counts_df)
                assignments_df = signatures.get_assignments(exps_df)
                # set region of genome
                ssm_df['region'] = ssm_df.apply(lambda row: row[POS_START] // region_width * region_width, axis=1)
                # add signature column
                # TODO: figure out why this step takes so long
                ssm_df['signature'] = ssm_df.apply(lambda row: assignments_df.loc[row[SAMPLE], row[cat_colname]] if pd.notnull(row[cat_colname]) else None, axis=1)
                # for each chromosome
                for chr_name, ssm_chr_df in ssm_df.groupby([CHR]):
                    # aggregate
                    groups = ssm_chr_df.groupby(['region', 'signature'])
                    counts = groups.size().reset_index(name='counts')   
                    regions_df = counts.pivot(index='signature', columns='region', values='counts')
                    # sum
                    chr_dfs[str(chr_name)][mut_type] = chr_dfs[str(chr_name)][mut_type].add(regions_df, fill_value=0)
        
    # finalize
    for chr_name in CHROMOSOMES.keys():
        for mut_type in MUT_TYPES:
            chr_dfs[chr_name][mut_type].fillna(value=0, inplace=True)
            chr_dfs[chr_name][mut_type][list(chr_dfs[chr_name].columns.values)] = chr_dfs[chr_name][mut_type][list(chr_dfs[chr_name].columns.values)].astype(int)
            chr_dfs[chr_name][mut_type] = chr_dfs[chr_name][mut_type].transpose().to_dict(orient='index')
    return chr_dfs