from sqlalchemy.sql import text
from sqlalchemy import String
from sqlalchemy.dialects.mysql import MEDIUMINT

from web_constants import *


def plot_counts(conn, projects, single_sample_id=None):
    if single_sample_id != None: # single sample request
        samples = [single_sample_id]
        return [] # TODO: write the sql query for the single-sample case

    where_clause = " OR ".join([ f"project.name = :project_name_{i}" for i in range(len(projects)) ])

    query = f"""
        SELECT 
            samples_by_proj.sample_name, 
            mut_cat_type.name AS mut_cat_type_name,
            COALESCE(mut_counts_by_cat_type.mut_cat_type_count, 0) AS mut_cat_type_count_val
        FROM (
            SELECT 
                sample.id AS sample_id, 
                CONCAT(project.name, " ", sample.sample_name) AS sample_name
            FROM sample 
            LEFT JOIN project
                ON project.id = sample.project_id
            WHERE {where_clause}
        ) AS samples_by_proj
        CROSS JOIN mut_cat_type
        LEFT JOIN (
            SELECT 
                mut_count_by_proj.sample_id, 
                SUM(mut_count_by_proj.value) AS mut_cat_type_count, 
                mut_cat.cat_type_id AS mut_cat_type_id
            FROM (
                SELECT 
                    samples_by_proj_2.sample_id, 
                    mut_count.cat_id, 
                    mut_count.value
                FROM (
                    SELECT 
                        sample.id AS sample_id
                    FROM sample 
                    WHERE sample.project_id IN (
                        SELECT project.id 
                        FROM project 
                        WHERE {where_clause}
                    )
                ) AS samples_by_proj_2
                LEFT JOIN mut_count
                    ON mut_count.sample_id = samples_by_proj_2.sample_id
            ) AS mut_count_by_proj
            INNER JOIN mut_cat
                ON mut_cat.id = mut_count_by_proj.cat_id
            GROUP BY mut_count_by_proj.sample_id, mut_cat_type_id
        ) AS mut_counts_by_cat_type
            ON 
                mut_counts_by_cat_type.sample_id = samples_by_proj.sample_id 
                AND mut_counts_by_cat_type.mut_cat_type_id = mut_cat_type.id
    """

    params = dict([(f"project_name_{i}", projects[i]) for i in range(len(projects))])

    stmt = text(query)
    stmt = stmt.bindparams(**params)
    """stmt = stmt.columns(
        sample_name_with_proj=String, 
        mut_cat_type_name=String, 
        mut_cat_type_count=MEDIUMINT
    )"""

    db_result = conn.execute(stmt)

    result = []

    curr_sample = None
    for row in db_result:
        # ASSUMING THE ROWS ARE ORDERED BY SAMPLE, THEN BY CAT_TYPE,
        # we will see the rows for each sample consecutively.
        if curr_sample == row[0]:
            result[-1][row[1]] = int(row[2])
        else:
            result.append({
                "sample_id": row[0],
                row[1]: int(row[2])
            })
            curr_sample = row[0]
    
    return result


if __name__ == "__main__":
    from pprint import pprint
    from db import db_connect

    engine, conn = db_connect()
    result = plot_counts(conn, projects=[
        'ICGC-ORCA-IN_ORCA_27.WXS',
        'ICGC-BRCA-EU_BRCA_27.WGS'
    ])

    pprint(result)