import pandas as pd
import numpy as np

from web_constants import *
from project_data import ProjectData, get_project_data
from helpers import pd_as_file


dtype = {
    SAMPLE: str,
    CHR: str,
    POS_START: int,
    CAT_SBS_96: str,
    MUT_DIST: float,
    MUT_DIST_ROLLING_MEAN: float
}

def plot_rainfall(proj_id, sample_id):
    proj = get_project_data(proj_id)

    df_cols = [SAMPLE, CHR, POS_START, CAT_SBS_96, MUT_DIST, MUT_DIST_ROLLING_MEAN]
    ssm_df = pd.DataFrame([], columns=df_cols)

    mut_type = 'SBS' # restricting to SBS for now
    # TODO: update to include other mutation types later?

    ssm_df = proj.get_extended_df(mut_type, dtype=dtype, usecols=dtype.keys())
    ssm_df = ssm_df.loc[ssm_df[SAMPLE] == sample_id][df_cols].copy()

    ssm_df['kataegis'] = ssm_df.apply(lambda row: 1 if (row[MUT_DIST_ROLLING_MEAN] <= 1000) else 0, axis=1)
    ssm_df = ssm_df.drop(columns=[MUT_DIST_ROLLING_MEAN, SAMPLE])
    ssm_df = ssm_df.replace([np.inf, -np.inf], np.nan)
    ssm_df = ssm_df.dropna(axis=0, how='any', subset=[CAT_SBS_96, MUT_DIST])
    ssm_df[MUT_DIST] = ssm_df[MUT_DIST].astype(int)
    ssm_df = ssm_df.rename(columns={ CHR: "chr", POS_START: "pos", CAT_SBS_96: "cat", MUT_DIST: "mut_dist" })
    return pd_as_file(ssm_df, index_val=False)