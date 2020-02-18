import pandas as pd
import numpy as np

from web_constants import *
from project_data import ProjectData, get_selected_project_data


def scale_counts(projects, single_sample_id=None, count_sum=False):
    result = [0, 0]

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
        proj_counts_df.index = proj_counts_df.index.rename("sample_id")

        for mut_type in MUT_TYPES:
            counts_df = proj.get_counts_df(mut_type)

            counts_df = counts_df.sum(axis=1).to_frame().rename(columns={0:mut_type})
            proj_counts_df = proj_counts_df.join(counts_df, how='outer')
            proj_counts_df = proj_counts_df.fillna(value=0)
        
        if count_sum:
            proj_counts_df = proj_counts_df.sum(axis=1)
            proj_counts_df_max = proj_counts_df.max()
        else:
            proj_counts_df_max = proj_counts_df.max().max()

        result[1] = max(result[1], proj_counts_df_max)

    return result

# If for all mutation types
"""
SELECT MAX(mut_cat_type_count) AS max_sample_mut_count
FROM (
    SELECT 
        mut_count_by_proj.sample_id, 
        SUM(mut_count_by_proj.value) AS mut_cat_type_count
    FROM (
        SELECT 
            samples_by_proj.sample_id, 
            mut_count.cat_id, 
            mut_count.value
        FROM (
            SELECT 
                sample.id AS sample_id
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
) AS mut_count_by_proj_by_sample
"""

# If for particular mutation type
"""
SELECT 
	MAX(mut_count_by_cat_type.mut_cat_type_count) AS max_sample_mut_count
FROM (
    SELECT 
    	mut_count_by_proj.sample_id, 
    	SUM(mut_count_by_proj.value) AS mut_cat_type_count, 
    	mut_cat.cat_type_id AS mut_cat_type_id
    FROM (
    	SELECT samples_by_proj.sample_id, samples_by_proj.sample_name, mut_count.cat_id, mut_count.value
        FROM (
            SELECT sample.id AS sample_id, sample.sample_name AS sample_name
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
    INNER JOIN mut_cat
        ON mut_cat.id = mut_count_by_proj.cat_id
    GROUP BY mut_count_by_proj.sample_id, mut_cat_type_id
) AS mut_count_by_cat_type
WHERE mut_count_by_cat_type.mut_cat_type_id = (
    SELECT id 
    FROM mut_cat_type 
    WHERE mut_cat_type.name = 'SBS_96'
)
"""