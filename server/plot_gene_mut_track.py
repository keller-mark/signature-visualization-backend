import pandas as pd
import numpy as np

from web_constants import *
from project_data import ProjectData, get_selected_project_data

from helpers import pd_fetch_tsv

MUT_CLASS_PRIORITIES = [
    MUT_CLASS_VALS.SILENT.value, 
    MUT_CLASS_VALS.OTHER.value,
    MUT_CLASS_VALS.TRANSLATION_START_SITE.value,
    MUT_CLASS_VALS.SPLICE_SITE.value,
    MUT_CLASS_VALS.MISSENSE.value,
    MUT_CLASS_VALS.IN_FRAME_INDEL.value,
    MUT_CLASS_VALS.NONSTOP.value,
    MUT_CLASS_VALS.NONSENSE.value,
    MUT_CLASS_VALS.FRAMESHIFT.value
]

def convert_mut_class_to_priority(val):
    if pd.isna(val):
        return -1
    if val in MUT_CLASS_PRIORITIES:
        return MUT_CLASS_PRIORITIES.index(val)
    return -1

def plot_gene_mut_track(gene_id, projects):
    result = []
    
    project_data = get_selected_project_data(projects)
    for proj in project_data:
        proj_id = proj.get_proj_id()
        samples = proj.get_samples_list()

        proj_result_df = pd.DataFrame(index=samples, columns=[])
        proj_result_df.index.rename("sample_id", inplace=True)

        mut_df = proj.get_gene_mut_df()
        if mut_df is not None:
            mut_df = mut_df.loc[mut_df[GENE_SYMBOL] == gene_id][[SAMPLE, MUT_CLASS]]
            mut_df["priority"] = mut_df[MUT_CLASS].apply(convert_mut_class_to_priority).astype(int)
            mut_df = mut_df.sort_values(by=["priority"], ascending=True)
            mut_df = mut_df.drop_duplicates(subset=[SAMPLE], keep='last')
            mut_df = mut_df.drop(labels=['priority'], axis='columns')
            mut_df = mut_df.rename(columns={SAMPLE: "sample_id", MUT_CLASS: "mut_class"})
            mut_df = mut_df.set_index("sample_id", drop=True)
            
            proj_result_df = proj_result_df.join(mut_df, how='outer')

        proj_result_df = proj_result_df.reset_index()
        proj_result_df = proj_result_df.fillna(value="None")
        proj_result = proj_result_df.to_dict('records')
        result = (result + proj_result)
        
    return result
  


def autocomplete_gene(gene_id_partial, projects):
    gene_id_partial = gene_id_partial.upper()
    first_letter = gene_id_partial[0]

    genes_agg_df = pd.read_csv(GENES_AGG_FILE.format(letter=first_letter), sep='\t')
    genes_agg_df = genes_agg_df.loc[genes_agg_df[META_COL_PROJ].isin(projects)]

    gene_list = genes_agg_df[GENE_SYMBOL].unique().tolist()

    gene_list_filtered = list(filter(lambda gene_id: gene_id.startswith(gene_id_partial), gene_list))
    return gene_list_filtered

def plot_pathways_listing():
    result = []
    meta_df = pd.read_csv(META_PATHWAYS_FILE, sep="\t", index_col=0)
    for group, group_row in meta_df.iterrows():
        group_df = pd_fetch_tsv(OBJ_DIR, group_row[META_COL_PATH_PATHWAYS])
        for index, row in group_df.iterrows():
            row_dict = {
                "publication": group_row["Publication"],
                "pathway_group": group,
                "gene": row[GENE_SYMBOL],
                "pathway": row["Pathway"],
                "core": row["Core"]
            }
            if hasattr(row, "Location"):
                row_dict["location"] = row["Location"]
            if hasattr(row, "Gene Description"):
                row_dict["description"] = row["Gene Description"]
            if hasattr(row, "Core"):
                row_dict["core"] = row["Core"]
            else:
                row_dict["core"] = False
            result.append(row_dict)
    return result


# Gene mutations for particular project and gene
"""
SELECT gene.name AS gene_name, sample.sample_name AS sample_name, gene_mut_class.name AS gene_mut_class_name
FROM (
    SELECT gene_mut_val.gene_id, gene_mut_val.sample_id, gene_mut_val.mut_class_id 
    FROM gene_mut_val 
    WHERE 
        gene_mut_val.gene_id = (
            SELECT id 
            FROM gene 
            WHERE gene.name = 'BRCA1'
        )
        AND gene_mut_val.sample_id IN (
            SELECT id 
            FROM sample 
            WHERE sample.project_id = (
                SELECT id 
                FROM project 
                WHERE project.name = 'ICGC-ORCA-IN_ORCA_27.WXS'
            )
        )
) AS gene_mut_vals_of_interest
LEFT JOIN gene
	ON gene.id = gene_mut_vals_of_interest.gene_id
LEFT JOIN sample
	ON sample.id = gene_mut_vals_of_interest.sample_id
LEFT JOIN gene_mut_class
	ON gene_mut_class.id = gene_mut_vals_of_interest.mut_class_id
"""


# Autocomplete gene
"""
SELECT gene.name FROM gene WHERE gene.name LIKE 'BR%'
"""
# or
"""
session.Query(Gene).where(Gene.name.startswith('BR'))
"""


# Pathway gene listing
"""
SELECT 
    pathway_group.name AS pathway_group_name, 
    pathway_group.publication, 
    pathway.name AS pathway_name, 
    gene.name AS gene_name, 
    pathway_gene.is_core
FROM pathway_gene
LEFT JOIN gene
	ON gene.id = pathway_gene.gene_id
LEFT JOIN pathway
	ON pathway.id = pathway_gene.pathway_id
LEFT JOIN pathway_group
	ON pathway_group.id = pathway.group_id
"""