import pandas as pd
import numpy as np
from web_constants import *
from plot_processing import *

dtype = {
    SAMPLE: str,
    CHR: str,
    POS_START: int,
    MUT_DIST_ROLLING_MEAN: float
}

def plot_kataegis(projects):
    width = 1000
    df_cols = [SAMPLE, CHR, POS_START]
    df = pd.DataFrame([], columns=df_cols)
    result = {
      # sets of kataegis mutations by donor, chromosome
      # 'SAMPLE': { '1': list(mutation_1, mutation_2), ... }
    }
    project_metadata = PlotProcessing.project_metadata()
    for proj_id in projects:
        if project_metadata[proj_id][HAS_SSM]:
            ssm_filepath = project_metadata[proj_id]["extended_sbs_path"]
            ssm_df = PlotProcessing.pd_fetch_tsv(ssm_filepath, dtype=dtype, usecols=dtype.keys())
            katagis_df = ssm_df.loc[ssm_df[MUT_DIST_ROLLING_MEAN] <= width][df_cols]
            df = df.append(katagis_df, ignore_index=True)
            # create empty entry for each donor
            proj_donor_ids = list(ssm_df[SAMPLE].unique())
            for donor_id in proj_donor_ids:
                result[donor_id] = { 'kataegis': {}, 'proj_id': proj_id }
    
    groups = df.groupby([SAMPLE, CHR])
    def add_group(g):
        g_donor_id = g[SAMPLE].unique()[0]
        g_chromosome = g[CHR].unique()[0]
        g_kataegis_mutations = list(g[POS_START].unique())
        result[g_donor_id]['kataegis'][g_chromosome] = g_kataegis_mutations

    groups.apply(add_group)

    return result