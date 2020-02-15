import pandas as pd
import numpy as np
import subprocess
import os
import sys
import json
import string

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import (
    SequencingType,
    ProjectSource,
    Project,
    Sample,
    MutationCategoryType
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

def read_tsv(csv_file_path, **kwargs):
    return pd.read_csv(os.path.join(OBJ_DIR, csv_file_path), sep='\t', **kwargs)

def anull(v):
    if not pd.notnull(v):
        return None
    return v


def load_oncotree():
    with open(ONCOTREE_FILE) as f:
        tree_json = json.load(f)
        return OncoTree(tree_json)

def create_project_sources(session, data_df):
    names = data_df[META_COL_PROJ_SOURCE].unique()
    return [ ProjectSource(name=name) for name in names ]

def get_project_source_id(session, name):
    return session.query(ProjectSource).filter(
        ProjectSource.name == name
    ).one().id

def create_seq_types(session, data_df):
    names = data_df[META_COL_PROJ_SEQ_TYPE].unique()
    return [ SequencingType(name=name) for name in names ]

def get_seq_type_id(session, name):
    return session.query(SequencingType).filter(
        SequencingType.name == name
    ).one().id

def create_projects(session, data_df):
    d = []
    for i, row in data_df.iterrows():
        d.append(
            Project(
                name=row[META_COL_PROJ],
                name_nice=row[META_COL_PROJ_NAME],
                source_id=get_project_source_id(session, row[META_COL_PROJ_SOURCE]),
                seq_type_id=get_seq_type_id(session, row[META_COL_PROJ_SEQ_TYPE]),
                oncotree_code=anull(row[META_COL_ONCOTREE_CODE])
            )
        )
    return d

def get_project_id(session, name):
    return session.query(Project).filter(
        Project.name == name
    ).one().id

def create_samples(session, data_df):
    d = []
    for i, d_row in data_df.iterrows():
        project_id = get_project_id(session, d_row[META_COL_PROJ])
        samples_df = read_tsv(d_row[META_COL_PATH_SAMPLES])
        for j, s_row in samples_df.iterrows():
            d.append(
                Sample(
                    project_id=project_id,
                    sample_name=s_row[SAMPLE],
                    patient_name=s_row[PATIENT]
                )
            )
    return d

def get_sample_id(session, name):
    return session.query(Sample).filter(
        Sample.sample_name == name
    ).one().id



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
        print('* Successfully connected to database')
    except Exception as e:
        print(e)
        print('* Unable to connect to database')
    

    # Get the session
    Session = sessionmaker(bind=connection)
    session = Session()

    # Clear all tables that are about to be filled
    # DO NOT CLEAR SESSION, WORKFLOW, OR USER TABLES
    session.query(MutationCategoryType).delete()
    session.query(Sample).delete()
    session.query(Project).delete()
    session.query(ProjectSource).delete()
    session.query(SequencingType).delete()
    session.commit()

    # Fill tables
    project_sources = create_project_sources(session, data_df)
    session.add_all(project_sources)
    session.commit()

    seq_types = create_seq_types(session, data_df)
    session.add_all(seq_types)
    session.commit()

    projects = create_projects(session, data_df)
    session.add_all(projects)
    session.commit()

    samples = create_samples(session, data_df)
    session.add_all(samples)
    session.commit()

    session.commit()

    print('* Done filling')