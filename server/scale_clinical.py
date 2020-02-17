import pandas as pd
import numpy as np
import pickle

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

from plot_clinical import plot_clinical, get_clinical_variables, meta_clinical_df

def clinical_var_infer_extent(clinical_var, meta_clinical_df):
    return (meta_clinical_df.loc[(meta_clinical_df[META_COL_CLINICAL_COL] == clinical_var) & \
            (meta_clinical_df[META_COL_CLINICAL_EXTENT] == 'infer')].shape[0] > 0)

def clinical_var_is_continuous(clinical_var, meta_clinical_df):
    return (meta_clinical_df.loc[(meta_clinical_df[META_COL_CLINICAL_COL] == clinical_var) & \
            (meta_clinical_df[META_COL_CLINICAL_SCALE_TYPE] == 'continuous')].shape[0] > 0)

def clear_list_of_nan(l):
    return list(set(l) - set(['nan']))

def scale_clinical(projects):
    result = {}
    clinical_df = plot_clinical(projects, return_df=True)
    for clinical_var in get_clinical_variables():
        if clinical_var_infer_extent(clinical_var, meta_clinical_df):
            if clinical_var_is_continuous(clinical_var, meta_clinical_df):
                # infer and continuous
                result[clinical_var] = [clinical_df[clinical_var].min(), clinical_df[clinical_var].max()]
                # If NaN values, just use 0 and 1
                if pd.isna(result[clinical_var][0]) and pd.isna(result[clinical_var][1]):
                    result[clinical_var][0] = 0
                    result[clinical_var][1] = 1
            else:
                # infer and categorical
                result[clinical_var] = sorted(clear_list_of_nan(list(clinical_df[clinical_var].unique())))
        else:
            clinical_values = meta_clinical_df.loc[meta_clinical_df[META_COL_CLINICAL_COL] == clinical_var][META_COL_CLINICAL_VALUE]
            if clinical_var_is_continuous(clinical_var, meta_clinical_df):
                # provided values and continuous
                clinical_values = clinical_values.astype(float)
                result[clinical_var] = [clinical_values.min(), clinical_values.max()]
            else:
                # provided values and categorical
                result[clinical_var] = list(clinical_values.unique())
    
    return result

"""
SELECT clinical_var_val.clinical_var_id, clinical_var_val.value, clinical_var.name, clinical_var.scale_type
FROM clinical_var_val
LEFT JOIN clinical_var
	ON clinical_var.id = clinical_var_val.clinical_var_id
ORDER BY clinical_var_val.id ASC
"""
