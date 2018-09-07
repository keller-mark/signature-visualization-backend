import pandas as pd
import numpy as np
import pickle

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

def plot_genome_event_track(gene_id, projects):
    result = {}
    
    project_data = get_selected_project_data(projects)
    for proj in project_data:
        proj_id = proj.get_proj_id()
        samples = proj.get_samples_list()
        events_df = proj.get_events_df()

        gene_events_df = events_df.loc[events_df['gene_id'] == gene_id]
        gene_events_df = gene_events_df.set_index('sample_id')

        event_codes = {
            "0": "NA",
            "1": "germ_bi_patho",
            "2": "germ_bi_patho_double",
            "3": "germ_bi_vus",
            "4": "event_4", # TODO
            "5": "som_bi_patho",
            "6": "som_bi_patho_double",
            "7": "som_bi_vus",
            "8": "som_loh",
            "9": "event_9", # TODO
            "10": "event_10" # TODO
        }

        # TODO: change from donors to samples
        for sample_id in samples:
            try:
                event = gene_events_df.loc[sample_id]['event_type']
            except KeyError:
                event = 0

            result[sample_id] = {
                "sample_id": sample_id,
                "proj_id": proj_id,
                "event": event_codes[str(event)]
            }
    return result
  


def autocomplete_gene(gene_id_partial):
    gene_id_partial = gene_id_partial.upper()
    with open(GENE_LIST_FILE, 'rb') as f:
        gene_list = pickle.load(f)
        gene_list_filtered = list(filter(lambda gene_id: gene_id.startswith(gene_id_partial), gene_list))
    return gene_list_filtered