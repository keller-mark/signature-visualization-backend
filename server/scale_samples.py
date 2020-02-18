import pandas as pd

from web_constants import *
from project_data import ProjectData, get_selected_project_data


def scale_samples(projects):
    project_data = get_selected_project_data(projects)
    result_series = pd.concat([proj.get_counts_sum_series() for proj in project_data])
    result_series = result_series.sort_values(ascending=False)
    return list(result_series.index.values)

"""
SELECT 
	sample_count_sum.sample_name,
    project.name AS project_name
FROM (
	SELECT 
        mut_count_by_proj.sample_name,
    	mut_count_by_proj.project_id,
        SUM(mut_count_by_proj.value) AS mut_cat_type_count
    FROM (
        SELECT 
            samples_by_proj.sample_id, 
        	samples_by_proj.sample_name,
        	samples_by_proj.project_id,
            mut_count.cat_id, 
            mut_count.value
        FROM (
            SELECT 
                sample.id AS sample_id,
            	sample.sample_name AS sample_name,
            	sample.project_id AS project_id
            FROM sample 
            WHERE sample.project_id IN (
                SELECT project.id 
                FROM project 
                WHERE project.name = 'ICGC-ORCA-IN_ORCA_27.WXS'
            )
        ) AS samples_by_proj
        LEFT JOIN mut_count
            ON mut_count.sample_id = samples_by_proj.sample_id
    ) AS mut_count_by_proj
    GROUP BY sample_id
) AS sample_count_sum
LEFT JOIN project
	ON project.id = sample_count_sum.project_id
ORDER BY sample_count_sum.mut_cat_type_count DESC
"""