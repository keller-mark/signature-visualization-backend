import pandas as pd
import numpy as np
import pickle

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

def plot_gene_event_track(gene_id, projects):
    result = []
    
    project_data = get_selected_project_data(projects)
    for proj in project_data:
        proj_id = proj.get_proj_id()
        samples = proj.get_samples_list()

        proj_result_df = pd.DataFrame(index=samples, columns=[])
        proj_result_df.index.rename("sample_id", inplace=True)

        events_df = proj.get_events_df()
        if events_df is not None:
            gene_events_df = events_df.loc[events_df[GENE_SYMBOL] == gene_id][[SAMPLE, MUT_CLASS]]
            gene_events_df = gene_events_df.rename(columns={SAMPLE: "sample_id", MUT_CLASS: "mut_class"})
            gene_events_df = gene_events_df.set_index("sample_id", drop=True)
            
            proj_result_df = proj_result_df.join(gene_events_df, how='outer')

        proj_result_df = proj_result_df.reset_index()
        proj_result_df = proj_result_df.fillna(value="None")
        proj_result = proj_result_df.to_dict('records')
        result = (result + proj_result)
        
    return result
  


def autocomplete_gene(gene_id_partial, projects):
    gene_id_partial = gene_id_partial.upper()

    genes_agg_df = pd.read_csv(GENES_AGG_FILE, sep='\t')
    genes_agg_df = genes_agg_df.loc[genes_agg_df["proj_id"].isin(projects)]

    gene_list = genes_agg_df[GENE_SYMBOL].unique().tolist()

    gene_list_filtered = list(filter(lambda gene_id: gene_id.startswith(gene_id_partial), gene_list))
    return gene_list_filtered