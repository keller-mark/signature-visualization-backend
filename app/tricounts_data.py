import pandas as pd
import json
from web_constants import *
from helpers import pd_fetch_tsv, path_or_none

""" Load tri-counts data """
tricounts_dfs = {}
tricounts_meta_df = pd.read_csv(META_TRICOUNTS_FILE, sep='\t', index_col=0)
for tricounts_method, tricounts_row in tricounts_meta_df.iterrows():
    tricounts_dfs[tricounts_method] = pd_fetch_tsv(OBJ_DIR, tricounts_row[META_COL_PATH_TRICOUNTS])

def get_tricounts_methods():
    return list(tricounts_dfs.keys())

def get_tricounts_df(tricounts_method):
    return tricounts_dfs[tricounts_method]