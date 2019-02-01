import pandas as pd
import numpy as np
import pickle

from web_constants import *
from project_data import ProjectData, get_selected_project_data

# Read in meta file
meta_clinical_df = pd.read_csv(META_CLINICAL_FILE, sep='\t')
meta_clinical_df = meta_clinical_df.loc[~meta_clinical_df[META_COL_CLINICAL_COL].isin([ICD_O_3_SITE_DESC, ICD_O_3_HISTOLOGY_DESC, SURVIVAL_DAYS_TO_DEATH, SURVIVAL_DAYS_TO_LAST_FOLLOWUP])]

def append_icd_desc(row, code_col, desc_col):
    if row[desc_col] != 'nan':
        return ("%s (%s)" % (row[code_col], row[desc_col]))
    else:
        return row[code_col]

def plot_clinical_variables():
    return list(meta_clinical_df[META_COL_CLINICAL_COL].unique())

def plot_clinical_scale_types():
    return meta_clinical_df.drop_duplicates(subset=[META_COL_CLINICAL_COL])[[META_COL_CLINICAL_COL, META_COL_CLINICAL_SCALE_TYPE]].to_dict('records')

def plot_clinical(projects, return_df=False):
    result = []

    clinical_vars = plot_clinical_variables()
    project_data = get_selected_project_data(projects)

    clinical_df = pd.DataFrame(index=[], data=[], columns=clinical_vars + [ICD_O_3_SITE_DESC, ICD_O_3_HISTOLOGY_DESC])
    for proj in project_data:
        samples = proj.get_samples_list()
        if proj.has_clinical_df():
            proj_clinical_df = proj.get_clinical_df()
        else:
            proj_clinical_df = pd.DataFrame(index=samples, data=[], columns=[])
        clinical_df = clinical_df.append(proj_clinical_df, ignore_index=False)

    # Try to convert columns to float if continuous-valued variables
    for clinical_var in clinical_vars:
        if meta_clinical_df.loc[(meta_clinical_df[META_COL_CLINICAL_COL] == clinical_var) & \
            (meta_clinical_df[META_COL_CLINICAL_SCALE_TYPE] == 'continuous')].shape[0] > 0:
            try:
                clinical_df[clinical_var] = clinical_df[clinical_var].astype(float)
            except:
                pass
        else:
            clinical_df[clinical_var] = clinical_df[clinical_var].fillna(value='nan')
    
    # "special" variable behavior
    if ICD_O_3_SITE_CODE in clinical_vars:
        clinical_df[ICD_O_3_SITE_CODE] = clinical_df.apply(
            lambda row: append_icd_desc(row, ICD_O_3_SITE_CODE, ICD_O_3_SITE_DESC), 
            axis='columns'
        )
    if ICD_O_3_HISTOLOGY_CODE in clinical_vars:
        clinical_df[ICD_O_3_HISTOLOGY_CODE] = clinical_df.apply(
            lambda row: append_icd_desc(row, ICD_O_3_HISTOLOGY_CODE, ICD_O_3_HISTOLOGY_DESC), 
            axis='columns'
        )
    
    if SURVIVAL_DAYS_TO_DEATH in clinical_vars:
        clinical_df[SURVIVAL_DAYS_TO_DEATH] = clinical_df[SURVIVAL_DAYS_TO_DEATH].clip(lower=0.0)
    if SURVIVAL_DAYS_TO_LAST_FOLLOWUP in clinical_vars:
        clinical_df[SURVIVAL_DAYS_TO_LAST_FOLLOWUP] = clinical_df[SURVIVAL_DAYS_TO_LAST_FOLLOWUP].clip(lower=0.0)
    
    clinical_df.index = clinical_df.index.rename("sample_id")
    clinical_df = clinical_df[clinical_vars]

    if return_df:
        return clinical_df
    
    clinical_df = clinical_df.fillna(value='nan')

    clinical_df = clinical_df.reset_index()
    result = clinical_df.to_dict('records')

    return result
  

