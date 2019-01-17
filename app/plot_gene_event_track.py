import pandas as pd
import numpy as np
import pickle

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

from helpers import pd_fetch_tsv

def plot_gene_event_track(gene_id, projects):
    result = []
    
    project_data = get_selected_project_data(projects)
    for proj in project_data:
        proj_id = proj.get_proj_id()
        samples = proj.get_samples_list()

        proj_result_df = pd.DataFrame(index=samples, columns=[])
        proj_result_df.index.rename("sample_id", inplace=True)

        events_df = proj.get_genes_df()
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
    first_letter = gene_id_partial[0]

    genes_agg_df = pd.read_csv(GENES_AGG_FILE.format(letter=first_letter), sep='\t')
    genes_agg_df = genes_agg_df.loc[genes_agg_df[META_COL_PROJ].isin(projects)]

    gene_list = genes_agg_df[GENE_SYMBOL].unique().tolist()

    gene_list_filtered = list(filter(lambda gene_id: gene_id.startswith(gene_id_partial), gene_list))
    return gene_list_filtered

def plot_pathways_listing():
    result = []
    meta_df = pd.read_csv(META_PATHWAYS_FILE, sep="\t", index_col=0)
    for group, group_row in meta_df.iterrows():
        group_df = pd_fetch_tsv(OBJ_DIR, group_row[META_COL_PATH_PATHWAYS])
        for index, row in group_df.iterrows():
            row_dict = {
                "publication": group_row["Publication"],
                "pathway_group": group,
                "gene": row[GENE_SYMBOL],
                "pathway": row["Pathway"],
                "core": row["Core"]
            }
            if hasattr(row, "Location"):
                row_dict["location"] = row["Location"]
            if hasattr(row, "Gene Description"):
                row_dict["description"] = row["Gene Description"]
            if hasattr(row, "Core"):
                row_dict["core"] = row["Core"]
            else:
                row_dict["core"] = False
            result.append(row_dict)
    return result