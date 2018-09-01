import pandas as pd
import numpy as np

from web_constants import *
from project_data import ProjectData, get_selected_project_data


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
    project_data = get_selected_project_data(projects)
    for proj in project_data:
        proj_id = proj.get_proj_id()
        mut_type = 'SBS' # restricting to SBS for now
        # TODO: update to include other mutation types later?

        ssm_df = proj.get_extended_df(mut_type, dtype=dtype, usecols=dtype.keys())
        kataegis_df = ssm_df.loc[ssm_df[MUT_DIST_ROLLING_MEAN] <= width][df_cols]
        df = df.append(kataegis_df, ignore_index=True)
        # create empty entry for each donor
        proj_sample_ids = proj.get_samples_list()
        for sample_id in proj_sample_ids:
            result[sample_id] = { 'kataegis': {}, 'proj_id': proj_id }
    
    groups = df.groupby([SAMPLE, CHR])
    def add_group(g):
        g_sample_id = g[SAMPLE].unique()[0]
        g_chromosome = g[CHR].unique()[0]
        g_kataegis_mutations = list(g[POS_START].unique())
        result[g_sample_id]['kataegis'][g_chromosome] = g_kataegis_mutations

    groups.apply(add_group)

    return result