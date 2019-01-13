import pandas as pd
import numpy as np
import pickle

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

clinical_scales = {
    TOBACCO_BINARY: ["Smoker", "Non-Smoker"], 
    TOBACCO_INTENSITY: [0, 100], 
    ALCOHOL_BINARY: ["Alcohol User", "Alcohol Nonuser"], 
    ALCOHOL_INTENSITY: [0, 100], 
    DIAGNOSIS_AGE: [0, 100], 
    SEX: ["Male", "Female"],
    VITAL_STATUS: ["Alive", "Dead"],
    RECURRENCE: ["Yes", "No"],
    RADIATION_THERAPY: ["Yes", "No"]
}

def append_icd_desc(row, code_col, desc_col):
    return ("%s (%s)" % (row[code_col], row[desc_col]))

def scale_clinical_track(clinical_var, projects):
    try:
        return clinical_scales[clinical_var]
    except KeyError:
        # If scale values have not been enumerated in the dict above,
        # attempt to get a list of all possible values from the set of unique values in the column itself
        project_data = get_selected_project_data(projects)
        clinical_df = pd.DataFrame(index=[], data=[], columns=[clinical_var])
        for proj in project_data:
            samples = proj.get_samples_list()
            if proj.has_clinical_df():
                proj_clinical_df = proj.get_clinical_df()
            else:
                proj_clinical_df = pd.DataFrame(index=samples, data=[], columns=[])
            clinical_df = clinical_df.append(proj_clinical_df, ignore_index=False)
        
        # If ICD code, try to append description column values
        clinical_columns = list(clinical_df.columns.values)
        if clinical_var == ICD_O_3_SITE_CODE:
            if (ICD_O_3_SITE_CODE in clinical_columns) and (ICD_O_3_SITE_DESC in clinical_columns):
                clinical_df[ICD_O_3_SITE_CODE] = clinical_df.apply(lambda row: append_icd_desc(row, ICD_O_3_SITE_CODE, ICD_O_3_SITE_DESC), axis='columns')
        elif clinical_var == ICD_O_3_HISTOLOGY_CODE:
            if (ICD_O_3_HISTOLOGY_CODE in clinical_columns) and (ICD_O_3_HISTOLOGY_DESC in clinical_columns):
                clinical_df[ICD_O_3_HISTOLOGY_CODE] = clinical_df.apply(lambda row: append_icd_desc(row, ICD_O_3_HISTOLOGY_CODE, ICD_O_3_HISTOLOGY_DESC), axis='columns')
        
        clinical_df = clinical_df.fillna(value='nan')
        clinical_vals = list(set(list(clinical_df[clinical_var].unique())) - set(['nan']))
        clinical_vals = sorted(clinical_vals)
        return clinical_vals


