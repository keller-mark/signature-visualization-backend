import pandas as pd
import subprocess
import os
import sys
import json
import string

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import (
    ProjectSource,
    Project,
    ProjectOncotreeMapping
)

# Load our modules
this_file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.normpath(this_file_path + '/../'))
from web_constants import *
from oncotree import *


OBJ_DIR = '../../obj' # TODO: remove
#OBJ_DIR = '/obj'

META_DATA_FILE = os.path.join(OBJ_DIR, META_DATA_FILENAME)
META_SIGS_FILE = os.path.join(OBJ_DIR, META_SIGS_FILENAME)
META_PATHWAYS_FILE = os.path.join(OBJ_DIR, META_PATHWAYS_FILENAME)
META_FEATURED_FILE = os.path.join(OBJ_DIR, META_FEATURED_FILENAME)
META_TRICOUNTS_FILE = os.path.join(OBJ_DIR, META_TRICOUNTS_FILENAME)

ONCOTREE_FILE = os.path.join(OBJ_DIR, ONCOTREE_FILENAME)

def load_oncotree():
    with open(ONCOTREE_FILE) as f:
        tree_json = json.load(f)
        return OncoTree(tree_json)


"""
def create_proj_to_sigs_mappings(data_df, sigs_df):
    print('* Mapping projects to signature cancer types by Oncotree codes')
    tree = load_oncotree()

    matches = []

    match_df = pd.DataFrame(index=[], data=[], columns=[META_COL_PROJ, META_COL_SIG_GROUP, META_COL_ONCOTREE_CODE])
    for data_index, data_row in data_df.iterrows():
        if pd.notnull(data_row[META_COL_ONCOTREE_CODE]):
            proj_node = tree.find_node(data_row[META_COL_ONCOTREE_CODE])
            if proj_node is not None:
                for sig_group_index, sig_group_row in sigs_df.iterrows():
                    if pd.notnull(sig_group_row[META_COL_PATH_SIGS_CANCER_TYPE_MAP]):
                        sig_group_cancer_type_map_df = read_tsv(sig_group_row[META_COL_PATH_SIGS_CANCER_TYPE_MAP])
                        cancer_type_map_codes = list(sig_group_cancer_type_map_df[META_COL_ONCOTREE_CODE].dropna().unique())
                        sig_group_parent_node = proj_node.find_closest_parent(cancer_type_map_codes)
                        if sig_group_parent_node is not None:
                            matches.append(
                                ProjectOncotreeMapping(
                                    
                                )
                            )
                            match_df = match_df.append({
                                META_COL_PROJ: data_row[META_COL_PROJ],
                                META_COL_SIG_GROUP: sig_group_row[META_COL_SIG_GROUP],
                                META_COL_ONCOTREE_CODE: sig_group_parent_node.code
                            }, ignore_index=True)
    match_df.to_csv(PROJ_TO_SIGS_FILE, index=False, sep='\t')
    return matches
"""


def create_project_sources(data_df):
    project_sources = []
    
    names = data_df[META_COL_PROJ_SOURCE].unique()
    for name in names:
        project_sources.append(
            ProjectSource(
                name=name
            )
        )

    return project_sources


if __name__ == "__main__":
    data_df = pd.read_csv(META_DATA_FILE, sep='\t')
    sigs_df = pd.read_csv(META_SIGS_FILE, sep='\t')
    pathways_df = pd.read_csv(META_PATHWAYS_FILE, sep='\t')
    tricounts_df = pd.read_csv(META_TRICOUNTS_FILE, sep='\t')

    # Connect to the db
    try:
        '''
        engine = create_engine("mysql://{user}:{password}@db:3306/explosig".format(
            user=os.environ['EXPLOSIG_DB_USER'],
            password=os.environ['EXPLOSIG_DB_PASSWORD']
        ))
        '''
        engine = create_engine("mysql://{user}:{password}@localhost:3306/explosig?unix_socket=/Applications/MAMP/tmp/mysql/mysql.sock".format(
            user='root',
            password='root'
        ))

        connection = engine.connect()
        print('* Successfully connected to database and created tables')
    except Exception as e:
        print(e)
        print('* Unable to connect to database')
    

    # Get the session
    Session = sessionmaker(bind=connection)
    session = Session()

    # Clear all tables that are about to be filled
    # DO NOT CLEAR SESSION, WORKFLOW, OR USER TABLES
    session.query(ProjectSource).delete()
    session.commit()

    # Fill tables
    project_sources = create_project_sources(data_df)
    session.add_all(project_sources)

    session.commit()

    print('* Done filling')