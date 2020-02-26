from sqlalchemy.sql import text
from sqlalchemy import String
from sqlalchemy.dialects.mysql import MEDIUMINT

from web_constants import *

# Regular counts matrix.
# Names of counts functions are confusing because plot_counts just considers mutation type e.g. for a sample, SBS: 1, DBS: 3, INDEL: 2
def plot_counts_by_category(conn, projects, mut_type, single_sample_id=None):
    if single_sample_id != None: # single sample request
        assert(len(projects) == 1)
        return [] # TODO: write the sql query for the single-sample case

    projects_where_clause = " OR ".join([ f"project.name = :project_name_{i}" for i in range(len(projects)) ])

    counts_query = f"""
    SELECT 
        mut_count_by_project.sample_name AS sample_name, 
        mut_cat.name, 
        COALESCE(mut_count_by_project.value, 0) AS mut_count_value
    FROM (
        SELECT 
            mut_count.sample_id, 
            CONCAT(project.name, " ", sample.sample_name) AS sample_name,
            mut_count.value,
            mut_count.cat_id
        FROM mut_count 
        LEFT JOIN sample
            ON sample.id = mut_count.sample_id
        LEFT JOIN project
            ON project.id = sample.project_id
        WHERE {projects_where_clause}
    ) AS mut_count_by_project
    LEFT JOIN mut_cat
        ON mut_cat.id = mut_count_by_project.cat_id
    WHERE mut_cat.cat_type_id = (
        SELECT mut_cat_type.id 
        FROM mut_cat_type 
        WHERE mut_cat_type.name = :mut_cat_type
    )
    ORDER BY sample_name ASC
    """

    projects_params = dict([(f"project_name_{i}", projects[i]) for i in range(len(projects))])
    cat_type_params = dict(mut_cat_type=MUT_TYPE_MAP[mut_type])

    counts_stmt = text(counts_query)
    counts_stmt = counts_stmt.bindparams(
        **projects_params, 
        **cat_type_params
    )

    db_result_counts = conn.execute(counts_stmt)

    cats_query = f"""
    SELECT 
        mut_cat.name
    FROM mut_cat 
    LEFT JOIN mut_cat_type
        ON mut_cat_type.id = mut_cat.cat_type_id
    WHERE mut_cat_type.name = :mut_cat_type
    """

    cats_stmt = text(cats_query)
    cats_stmt = cats_stmt.bindparams(**cat_type_params)

    db_result_cats = conn.execute(cats_stmt)
    cats_obj = dict([(c[0], 0) for c in db_result_cats])

    result = []
    
    curr_sample = None
    for row in db_result_counts:
        # ASSUMING THE ROWS ARE ORDERED BY SAMPLE
        if curr_sample == row[0]:
            result[-1][row[1]] = row[2]
        else:
            result.append(cats_obj.copy())
            result[-1]["sample_id"] = row[0]
            result[-1][row[1]] = row[2]

            curr_sample = row[0]

    return result

if __name__ == "__main__":
    from pprint import pprint
    from db import db_connect

    engine, conn = db_connect()
    result = plot_counts_by_category(conn, projects=[
        'ICGC-ORCA-IN_ORCA_27.WXS',
        'ICGC-BRCA-EU_BRCA_27.WGS'
    ], mut_type='SBS')

    pprint(result)

