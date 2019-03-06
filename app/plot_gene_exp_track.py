import pandas as pd
import numpy as np

from web_constants import *
from project_data import ProjectData, get_selected_project_data

from helpers import pd_fetch_tsv

def threshold_expression_values(val):
    if val <= -2:
        return "Under"
    if val >= 2:
        return "Over"
    if val in [-1, 0, 1]:
        return "Not differentially expressed"
    return "nan"

def plot_gene_exp_track(gene_id, projects):
    result = []
    
    project_data = get_selected_project_data(projects)
    for proj in project_data:
        proj_id = proj.get_proj_id()
        samples = proj.get_samples_list()

        proj_result_df = pd.DataFrame(index=samples, columns=[])
        proj_result_df.index.rename("sample_id", inplace=True)

        expr_df = proj.get_gene_exp_df()
        if expr_df is not None:
            expr_df = expr_df.loc[expr_df[GENE_SYMBOL] == gene_id][[SAMPLE, GENE_EXPRESSION_RNA_SEQ_MRNA_Z]]
            expr_df = expr_df.rename(columns={SAMPLE: "sample_id", GENE_EXPRESSION_RNA_SEQ_MRNA_Z: "gene_expression"})
            expr_df = expr_df.set_index("sample_id", drop=True)
            expr_df["gene_expression"] = expr_df["gene_expression"].apply(threshold_expression_values)
            
            proj_result_df = proj_result_df.join(expr_df, how='outer')

        proj_result_df = proj_result_df.reset_index()
        proj_result_df = proj_result_df.fillna(value="nan")
        proj_result = proj_result_df.to_dict('records')
        result = (result + proj_result)
        
    return result
  
