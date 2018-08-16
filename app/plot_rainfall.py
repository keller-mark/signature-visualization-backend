import pandas as pd
import numpy as np
from web_constants import *
from plot_processing import *

dtype = {
    SAMPLE: str,
    CHR: str,
    POS_START: int,
    CAT_SBS_96: str,
    MUT_DIST: float,
    MUT_DIST_ROLLING_MEAN: float
}

def plot_rainfall(proj_id, donor_id):
    project_metadata = PlotProcessing.project_metadata()

    df_cols = [SAMPLE, CHR, POS_START, CAT_SBS_96, MUT_DIST, MUT_DIST_ROLLING_MEAN]
    ssm_df = pd.DataFrame([], columns=df_cols)
    if project_metadata[proj_id][HAS_SSM]:
        ssm_filepath = project_metadata[proj_id]["extended_sbs_path"]
        
        ssm_df = PlotProcessing.pd_fetch_tsv(ssm_filepath, dtype=dtype, usecols=dtype.keys())
        ssm_df = ssm_df.loc[ssm_df[SAMPLE] == donor_id][df_cols].copy()

        ssm_df['kataegis'] = ssm_df.apply(lambda row: 1 if (row[MUT_DIST_ROLLING_MEAN] <= 1000) else 0, axis=1)
        ssm_df = ssm_df.drop(columns=[MUT_DIST_ROLLING_MEAN, SAMPLE])
        ssm_df = ssm_df.replace([np.inf, -np.inf], np.nan)
        ssm_df = ssm_df.dropna(axis=0, how='any', subset=[CAT_SBS_96, MUT_DIST])
        ssm_df[MUT_DIST] = ssm_df[MUT_DIST].astype(int)
        ssm_df = ssm_df.rename(columns={ CHR: "chr", POS_START: "pos", CAT_SBS_96: "cat", MUT_DIST: "mut_dist" })
    return PlotProcessing.pd_as_file(ssm_df, index_val=False)