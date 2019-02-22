import pandas as pd
import numpy as np

from web_constants import *
from project_data import ProjectData, get_selected_project_data

from helpers import pd_fetch_tsv

def plot_gene_cna_track(gene_id, projects):
    result = []
    
    project_data = get_selected_project_data(projects)
    for proj in project_data:
        proj_id = proj.get_proj_id()
        samples = proj.get_samples_list()

        proj_result_df = pd.DataFrame(index=samples, columns=[])
        proj_result_df.index.rename("sample_id", inplace=True)

        cna_df = proj.get_gene_cna_df()
        if cna_df is not None:
            cna_df = cna_df[[SAMPLE, gene_id]] # wide-formatted
            cna_df = cna_df.melt(id_vars=[SAMPLE], var_name=GENE_SYMBOL, value_name='copy_number')
            cna_df = cna_df.drop(labels=[GENE_SYMBOL], axis='columns')
            cna_df = cna_df.rename(columns={SAMPLE: "sample_id"})
            cna_df = cna_df.set_index("sample_id", drop=True)
            
            proj_result_df = proj_result_df.join(cna_df, how='outer')

        proj_result_df = proj_result_df.reset_index()
        proj_result_df = proj_result_df.fillna(value="None")
        proj_result = proj_result_df.to_dict('records')
        result = (result + proj_result)
        
    return result
  
