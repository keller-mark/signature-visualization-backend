import os
from web_constants import *
from signatures import Signatures
from project_data import ProjectData, get_all_project_data_as_json, get_all_tissue_types_as_json
from sig_data import SigData, get_all_sig_data_as_json, get_all_cancer_type_mappings_as_json
from plot_clinical import get_clinical_variable_scale_types


def plot_data_listing():
    return {
      "projects": get_all_project_data_as_json(),
      "signatures": get_all_sig_data_as_json(),
      "cancer_type_map": get_all_cancer_type_mappings_as_json(),
      "tissue_types": get_all_tissue_types_as_json(),
      "clinical_variable_scale_types": get_clinical_variable_scale_types()
    }

# Project data
"""
SELECT 
	project_source.name AS project_source,
	project.name, 
    project.name_nice, 
    project.oncotree_code,
    sample_count_by_project.sample_count
FROM project
LEFT JOIN project_source
	ON project_source.id = project.source_id
LEFT JOIN (
    SELECT sample.project_id, COUNT(id) AS sample_count
    FROM sample 
    GROUP BY sample.project_id
) AS sample_count_by_project
	ON sample_count_by_project.project_id = project.id
"""

# Signature data
"""
SELECT 
	CONCAT(sig_group.name, " ", sig.name) AS sig_name,
    sig.description AS sig_description,
    sig.index AS sig_index,
    sig_group.name AS sig_group_name,
    sig_group.publication AS sig_group_publication,
    mut_cat_type.name AS mut_cat_type_name,
    mut_type.name AS mut_type_name
FROM sig
LEFT JOIN sig_group
	ON sig_group.id = sig.group_id
LEFT JOIN mut_cat_type
	ON mut_cat_type.id = sig.cat_type_id
LEFT JOIN mut_type
	ON mut_type.id = mut_cat_type.mut_type_id
"""

# Cancer type data
"""
SELECT 
    CONCAT(sig_group.name, " ", sig.name) AS sig_name,
	sig_group.name AS sig_group_name,
    sig_oncotree_map.cancer_type AS cancer_type,
    sig_oncotree_map.oncotree_code AS oncotree_code
FROM sig_oncotree_map
LEFT JOIN sig
	ON sig.id = sig_oncotree_map.sig_id
LEFT JOIN sig_group
	ON sig_group.id = sig.group_id
"""

# Tissue type data
#   continue to get from the oncotree file

# Clinical variable scale type data
"""
SELECT
	clinical_var.name,
    clinical_var.scale_type
FROM clinical_var
"""