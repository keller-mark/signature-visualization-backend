import pandas as pd
import numpy as np

from web_constants import *
from project_data import ProjectData, get_selected_project_data


def plot_counts(projects, single_sample_id=None):
    result = []

    if single_sample_id != None: # single sample request
      assert(len(projects) == 1)
    
    project_data = get_selected_project_data(projects)
    for proj in project_data:
        proj_id = proj.get_proj_id()

        if single_sample_id != None: # single sample request
            samples = [single_sample_id]
        else:
            samples = proj.get_samples_list()

        proj_counts_df = pd.DataFrame(index=samples, columns=[])

        for mut_type in MUT_TYPES:
            counts_df = proj.get_counts_df(mut_type)

            counts_df = counts_df.sum(axis=1).to_frame().rename(columns={0:mut_type})
            proj_counts_df = proj_counts_df.join(counts_df, how='outer')
            proj_counts_df = proj_counts_df.fillna(value=0)
        
        proj_counts_df.index.rename("sample_id", inplace=True)
        
        proj_counts_df = proj_counts_df.reset_index()
        proj_result = proj_counts_df.to_dict('records')
        result = (result + proj_result)

    return result