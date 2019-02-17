import pandas as pd
import json
from web_constants import *
from helpers import pd_fetch_tsv, path_or_none

""" Load tri-counts data """
tricounts_dfs = {}
tricounts_meta_df = pd.read_csv(META_TRICOUNTS_FILE, sep='\t', index_col=0)
for tricounts_method, tricounts_row in tricounts_meta_df.iterrows():
    tricounts_dfs[tricounts_method] = pd_fetch_tsv(OBJ_DIR, tricounts_row[META_COL_PATH_TRICOUNTS], index_col=0)

def get_tricounts_methods():
    return list(tricounts_dfs.keys())

def get_tricounts_df(tricounts_method):
    return tricounts_dfs[tricounts_method]

def map_categories_to_trinucleotides(cat_type, categories):
    result = {}
    if cat_type == "SBS_96":
        # Assume category looks like A[C>T]G
        for cat in categories:
            trinucleotide = cat[0] + cat[2] + cat[6]
            result[cat] = trinucleotide
    else:
        pass
        # TODO Figure out how to map trinucleotides to double-base-substitution categories and indel categories
    return result

def get_tricounts_by_categories_df(cat_type, categories, tricounts_method):
    result_df = pd.DataFrame(index=[], data=[], columns=['Category', 'Trinucleotide', 'Count', 'Proportion'])
    cats_to_tris_map = map_categories_to_trinucleotides(cat_type, categories)
    tricounts_df = get_tricounts_df(tricounts_method)
    tricounts_sum = tricounts_df['Count'].sum()
    for cat, trinucleotide in cats_to_tris_map.items():
        count = tricounts_df.loc[trinucleotide, 'Count']
        proportion = count / tricounts_sum
        result_df = result_df.append({
            'Category': cat,
            'Trinucleotide': trinucleotide, 
            'Count': count, 
            'Proportion': proportion
        }, ignore_index=True)
    
    return result_df
