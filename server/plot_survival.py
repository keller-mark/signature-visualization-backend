import pandas as pd
import numpy as np
import pickle

from web_constants import *
from project_data import ProjectData, get_selected_project_data

def plot_survival(projects):
    result = []

    project_data = get_selected_project_data(projects)
    clinical_df = pd.DataFrame(index=[], data=[], columns=[SURVIVAL_DAYS_TO_DEATH, SURVIVAL_DAYS_TO_LAST_FOLLOWUP])
    for proj in project_data:
        samples = proj.get_samples_list()
        if proj.has_clinical_df():
            proj_clinical_df = proj.get_clinical_df()
        else:
            proj_clinical_df = pd.DataFrame(index=samples, data=[], columns=[])
        clinical_df = clinical_df.append(proj_clinical_df, ignore_index=False)
    clinical_df = clinical_df.fillna(value='nan')
    
    clinical_df.index = clinical_df.index.rename("sample_id")
    clinical_df = clinical_df[[SURVIVAL_DAYS_TO_DEATH, SURVIVAL_DAYS_TO_LAST_FOLLOWUP]]
    clinical_df = clinical_df.rename(columns={
        SURVIVAL_DAYS_TO_DEATH: "days_to_death",
        SURVIVAL_DAYS_TO_LAST_FOLLOWUP: "days_to_last_followup"
    })

    clinical_df = clinical_df.reset_index()
    result = clinical_df.to_dict('records')

    return result
  
"""
SELECT 
	sample.sample_name AS sample_name,
	clinical_var.name AS clinical_var_name,
    survival_val_by_project.value AS clinical_var_val
FROM (
    SELECT * 
    FROM clinical_val
    WHERE 
        clinical_var_id IN (
            SELECT id FROM clinical_var
            WHERE 
            	clinical_var.name = 'Days to Death' 
            	OR 
            	clinical_var.name = 'Days to Last Followup'
        )
    	AND
    	sample_id IN (
            SELECT id 
            FROM sample 
            WHERE sample.project_id IN (
                SELECT project.id 
                FROM project 
                WHERE project.name = 'ICGC-ORCA-IN_ORCA_27.WXS'
            )
        )
) AS survival_val_by_project
LEFT JOIN sample
	ON sample.id = survival_val_by_project.sample_id
LEFT JOIN clinical_var
	ON clinical_var.id = survival_val_by_project.clinical_var_id
"""