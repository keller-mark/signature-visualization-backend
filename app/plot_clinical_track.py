import pandas as pd
import numpy as np
import pickle

from web_constants import *
from project_data import ProjectData, get_selected_project_data

def append_icd_desc(row, code_col, desc_col):
    return ("%s (%s)" % (row[code_col], row[desc_col]))

def plot_clinical_track(clinical_var, projects):
    result = []

    project_data = get_selected_project_data(projects)
    clinical_df = pd.DataFrame(index=[], data=[], columns=[clinical_var])
    for proj in project_data:
        samples = proj.get_samples_list()
        if proj.has_clinical_df():
            proj_clinical_df = proj.get_clinical_df()
        else:
            proj_clinical_df = pd.DataFrame(index=samples, data=[], columns=[])
        clinical_df = clinical_df.append(proj_clinical_df, ignore_index=False)
    clinical_df = clinical_df.fillna(value='nan')

    # If ICD code, try to append description column values
    clinical_columns = list(clinical_df.columns.values)
    if clinical_var == ICD_O_3_SITE_CODE:
        if (ICD_O_3_SITE_CODE in clinical_columns) and (ICD_O_3_SITE_DESC in clinical_columns):
            clinical_df[ICD_O_3_SITE_CODE] = clinical_df.apply(lambda row: append_icd_desc(row, ICD_O_3_SITE_CODE, ICD_O_3_SITE_DESC), axis='columns')
    elif clinical_var == ICD_O_3_HISTOLOGY_CODE:
        if (ICD_O_3_HISTOLOGY_CODE in clinical_columns) and (ICD_O_3_HISTOLOGY_DESC in clinical_columns):
            clinical_df[ICD_O_3_HISTOLOGY_CODE] = clinical_df.apply(lambda row: append_icd_desc(row, ICD_O_3_HISTOLOGY_CODE, ICD_O_3_HISTOLOGY_DESC), axis='columns')
    
    clinical_df.index = clinical_df.index.rename("sample_id")
    clinical_df = clinical_df[[clinical_var]]
    clinical_df = clinical_df.rename(columns={clinical_var: ("cv_" + clinical_var)})

    clinical_df = clinical_df.reset_index()
    result = clinical_df.to_dict('records')

    return result
  

