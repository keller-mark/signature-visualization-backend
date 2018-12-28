import pandas as pd
import numpy as np
import pickle

from web_constants import *
from project_data import ProjectData, get_selected_project_data

def plot_clinical_track(clinical_var, projects):
    result = []
    
    project_data = get_selected_project_data(projects)
    for proj in project_data:
        proj_id = proj.get_proj_id()
        samples = proj.get_samples_list()

        proj_result_df = pd.DataFrame(index=samples, columns=[])
        proj_result_df.index.rename("sample_id", inplace=True)

        clinical_df = proj.get_clinical_df()
        if clinical_df is not None and clinical_var in list(clinical_df.columns.values):
            clinical_df.index.rename("sample_id", inplace=True)
            clinical_df = clinical_df[[clinical_var]]
            clinical_df = clinical_df.rename(columns={clinical_var: ("cv_" + clinical_var)})
            
            proj_result_df = proj_result_df.join(clinical_df, how='outer')

        proj_result_df = proj_result_df.reset_index()
        proj_result_df = proj_result_df.fillna(value="Unknown")
        proj_result = proj_result_df.to_dict('records')
        result = (result + proj_result)
        
    return result
  

