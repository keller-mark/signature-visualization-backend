import pandas as pd
import numpy as np

from web_constants import *
from project_data import ProjectData, get_project_data
from helpers import pd_as_file


dtype = {
    SAMPLE: str,
    CHR: str,
    POS_START: int,
    MUT_DIST: float,
    MUT_DIST_ROLLING_MEAN: float
}

def plot_rainfall(proj_id, sample_id):
    proj = get_project_data(proj_id)

    # still restricting to SBS for now
    # TODO: update to include other mutation types later...
    mut_type = 'SBS'
    cat_colname = SIG_TYPES[mut_type]
    dtype[cat_colname] = str
    
    df_cols = [SAMPLE, CHR, POS_START, cat_colname, MUT_DIST, MUT_DIST_ROLLING_MEAN]
    ssm_df = pd.DataFrame([], columns=df_cols)

    

    ssm_df = proj.get_extended_df(mut_type, dtype=dtype, usecols=dtype.keys())
    ssm_df = ssm_df.loc[ssm_df[SAMPLE] == sample_id][df_cols].copy()

    ssm_df['kataegis'] = ssm_df.apply(lambda row: 1 if (row[MUT_DIST_ROLLING_MEAN] <= 1000) else 0, axis=1)
    ssm_df = ssm_df.drop(columns=[MUT_DIST_ROLLING_MEAN, SAMPLE])
    ssm_df = ssm_df.replace([np.inf, -np.inf], np.nan)
    ssm_df = ssm_df.dropna(axis=0, how='any', subset=[cat_colname, MUT_DIST])
    ssm_df[MUT_DIST] = ssm_df[MUT_DIST].astype(int)
    ssm_df = ssm_df.rename(columns={ CHR: "chr", POS_START: "pos", cat_colname: "cat", MUT_DIST: "mut_dist" })
    return pd_as_file(ssm_df, index_val=False)