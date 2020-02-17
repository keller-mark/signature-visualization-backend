import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

from compute_counts import compute_counts
from scale_samples import scale_samples

# Get mutation counts by category (supports getting counts for a single sample)
def plot_counts_per_category(chosen_sigs, projects, mut_type, single_sample_id=None, normalize=False):
    result = []

    counts_df = compute_counts(chosen_sigs, projects, mut_type, single_sample_id=single_sample_id, normalize=normalize)
    counts_dict = counts_df.to_dict(orient='index')
    
    if single_sample_id == None:
        samples = scale_samples(projects)
    else:
        samples = [single_sample_id]

    def create_sample_obj(sample_id):
        sample_obj = counts_dict[sample_id]
        sample_obj["sample_id"] = sample_id
        return sample_obj

    result = list(map(create_sample_obj, samples))
    
    if single_sample_id != None: # single sample request
        result_obj = result[0]
        result = []
        for cat, value in result_obj.items():
            result.append({
                "cat_" + mut_type: cat,
                "count_" + mut_type + "_" + single_sample_id: value
            })

    return result


"""
SELECT 
	mut_cat_by_type.mut_cat_name,
    COALESCE(mut_count_by_sample.value, 0) AS mut_count_val
FROM (
    SELECT 
        mut_cat.id AS mut_cat_id, 
        mut_cat.name AS mut_cat_name 
    FROM mut_cat 
    WHERE mut_cat.cat_type_id = (SELECT mut_cat_type.id FROM mut_cat_type WHERE mut_cat_type.name = 'SBS_96')
) AS mut_cat_by_type
LEFT JOIN (
    SELECT *
    FROM mut_count
	WHERE mut_count.sample_id = (
        SELECT id 
        FROM sample WHERE (
            sample.sample_name = 'TCGA-OR-A5J1-01A-11D-A29I-10'
            AND sample.project_id = (SELECT id FROM project WHERE project.name = 'TCGA-ACC_ACC_mc3.v0.2.8.WXS')
        )
	)
) AS mut_count_by_sample
	ON mut_count_by_sample.cat_id = mut_cat_by_type.mut_cat_id
"""