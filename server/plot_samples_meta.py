import pandas as pd

from web_constants import *
from project_data import ProjectData, get_selected_project_data


def plot_samples_meta(projects):
    result = []
    project_data = get_selected_project_data(projects)
    for proj in project_data:
        proj_df = proj.get_samples_df()
        proj_list = proj.get_samples_list()
        proj_df = proj_df.reset_index()
        proj_df = proj_df.loc[proj_df[SAMPLE].isin(proj_list)]
        proj_df["proj_id"] = proj.get_proj_id()
        proj_df = proj_df.fillna(value="nan")
        proj_df = proj_df.rename(columns={
            SAMPLE: "sample_id",
            PATIENT: "donor_id"
        })
        proj_result = proj_df.to_dict('records')
        result = (result + proj_result)
    return result

"""
SELECT sample.sample_name AS sample_name, sample.patient_name AS patient_name
FROM sample 
WHERE sample.project_id IN (
	SELECT project.id 
	FROM project 
	WHERE project.name = 'ICGC-ORCA-IN_ORCA_27.WXS'
)
"""