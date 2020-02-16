import pandas as pd
import numpy as np
import subprocess
import os
import sys
import json
import string

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_

from models import (
    Base,
    SequencingType,
    ProjectSource,
    Project,
    Sample,
    MutationType,
    MutationCategoryType,
    MutationCategory,
    SignatureGroup,
    Signature,
    SignatureCategory,
    MutationCount,
    ClinicalVariable,
    ClinicalVariableValue,
    ClinicalValue,
    Gene,
    GeneExpressionValue,
    GeneExpressionValue,
    GeneMutationClass,
    GeneMutationValue,
    GeneCopyNumberValue,
    PathwayGroup,
    Pathway,
    PathwayGene,
    TrinucleotideCount,
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


# Hard-coded mutation and category types for now.
# In the future, a metadata file could allow these to be generalized.

CAT_TYPE_MAP = {
  'SBS': ['SBS_96'],
  'DBS': ['DBS_78'],
  'INDEL': ['INDEL_Alexandrov2018_83']
}

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

def create_samples_and_commit(engine, session, data_df):
    # TODO: clean up samples df by joining with counts df first
    for i, i_row in data_df.iterrows():
        d = []
        project_id = get_project_id(session, i_row[META_COL_PROJ])
        samples_df = read_tsv(i_row[META_COL_PATH_SAMPLES])
        for j, j_row in samples_df.iterrows():
            d.append(
                {
                    'project_id': project_id,
                    'sample_name': j_row[SAMPLE],
                    'patient_name': j_row[PATIENT]
                }
            )
        engine.execute(
            Sample.__table__.insert(),
            d
        )
        print(f'* Filled samples ({len(d)}) for project {i_row[META_COL_PROJ]}')
    return    

def get_sample_id(session, name, project_id):
    return session.query(Sample).filter(
        and_(
            Sample.sample_name == name,
            Sample.project_id == project_id
        )
    ).one().id

def create_mut_types(session):
    return [ MutationType(name=k) for k in CAT_TYPE_MAP.keys() ]

def get_mut_type_id(session, name):
    return session.query(MutationType).filter(
        MutationType.name == name
    ).one().id

def create_cat_types(session):
    d = []
    for mut_type, cat_types in CAT_TYPE_MAP.items():
        for cat_type in cat_types:
            d.append(
                MutationCategoryType(
                    name=cat_type,
                    mut_type_id=get_mut_type_id(session, mut_type)
                )
            )
    return d

def get_cat_type_id(session, name):
    return session.query(MutationCategoryType).filter(
        MutationCategoryType.name == name
    ).one().id

def create_cats(session, sigs_df):
    cat_type_to_cats = {}
    for i, i_row in sigs_df.iterrows():
        sigs_meta_df = read_tsv(i_row[META_COL_PATH_SIGS_META])
        for mut_type, cat_types in CAT_TYPE_MAP.items():
            for cat_type in cat_types:
                if cat_type not in cat_type_to_cats.keys() and pd.notnull(i_row[META_COL_PATH_SIGS_DATA.format(cat_type=cat_type)]):
                    sigs_data_df = read_tsv(i_row[META_COL_PATH_SIGS_DATA.format(cat_type=cat_type)], index_col=0)
                    cat_type_to_cats[cat_type] = sigs_data_df.columns.values.tolist()
    
    d = []
    for cat_type, cats in cat_type_to_cats.items():
        for cat in cats:
            d.append(
                MutationCategory(
                    name=cat,
                    cat_type_id=get_cat_type_id(session, cat_type)
                )
            )
    return d

def get_cat_id(session, name):
    return session.query(MutationCategory).filter(
        MutationCategory.name == name
    ).one().id


def generate_cat_to_id_map(session):
    cat_to_id_map = {}
    for mut_type, cat_types in CAT_TYPE_MAP.items():
        for cat_type in cat_types:
            cat_to_id_map[cat_type] = {}
            cats = session.query(MutationCategory).filter(
                MutationCategory.cat_type_id == get_cat_type_id(session, cat_type)
            )
            for cat in cats:
                cat_to_id_map[cat_type][cat.name] = cat.id
    return cat_to_id_map


def create_sig_groups(session, sigs_df):
    d = []
    for i, i_row in sigs_df.iterrows():
        d.append(
            SignatureGroup(
                name=i_row[META_COL_SIG_GROUP],
                publication=anull(i_row[META_COL_PUBLICATION])
            )
        )
    return d

def get_sig_group_id(session, name):
    return session.query(SignatureGroup).filter(
        SignatureGroup.name == name
    ).one().id

def create_sigs(session, sigs_df):
    d = []
    for i, i_row in sigs_df.iterrows():
        sigs_meta_df = read_tsv(i_row[META_COL_PATH_SIGS_META])
        for j, j_row in sigs_meta_df.iterrows():
            d.append(
                Signature(
                    name=j_row[META_COL_SIG],
                    index=anull(j_row[META_COL_INDEX]),
                    description=anull(j_row[META_COL_DESCRIPTION]),
                    cat_type_id=get_cat_type_id(session, j_row[META_COL_CAT_TYPE]),
                    group_id=get_sig_group_id(session, i_row[META_COL_SIG_GROUP])
                )
            )
    return d

def get_sig_id(session, name, group_id):
    return session.query(Signature).filter(
        and_(
            Signature.name == name,
            Signature.group_id == group_id
        )
    ).one().id



def create_sig_cats_and_commit(engine, session, sigs_df):
    cat_to_id_map = generate_cat_to_id_map(session)

    for i, i_row in sigs_df.iterrows():
        sigs_meta_df = read_tsv(i_row[META_COL_PATH_SIGS_META])
        sig_group_id = get_sig_group_id(session, i_row[META_COL_SIG_GROUP])
        d = []
        for mut_type, cat_types in CAT_TYPE_MAP.items():
            for cat_type in cat_types:
                if pd.notnull(i_row[META_COL_PATH_SIGS_DATA.format(cat_type=cat_type)]):
                    sigs_data_df = read_tsv(i_row[META_COL_PATH_SIGS_DATA.format(cat_type=cat_type)], index_col=0)
                    for j, j_row in sigs_data_df.iterrows():
                        sig_id = get_sig_id(session, j, sig_group_id)
                        for cat in sigs_data_df.columns.values.tolist():
                            d.append(
                                {
                                    'sig_id': sig_id,
                                    'cat_id': cat_to_id_map[cat_type][cat],
                                    'value': float(j_row[cat])
                                }
                            )
        engine.execute(
            SignatureCategory.__table__.insert(),
            d
        )
        print(f'* Filled sig cats ({len(d)}) for sig group {i_row[META_COL_SIG_GROUP]}')
    return


def create_mut_counts_and_commit(engine, session, data_df):
    cat_to_id_map = generate_cat_to_id_map(session)

    for i, i_row in data_df.iterrows():
        d = []
        project_id = get_project_id(session, i_row[META_COL_PROJ])
        seq_type_id = get_seq_type_id(session, i_row[META_COL_PROJ_SEQ_TYPE])
        for mut_type, cat_types in CAT_TYPE_MAP.items():
            for cat_type in cat_types:
                if pd.notnull(i_row[META_COL_PATH_MUTS_COUNTS.format(cat_type=cat_type)]):
                    counts_df = read_tsv(i_row[META_COL_PATH_MUTS_COUNTS.format(cat_type=cat_type)], index_col=0)
                    for j, j_row in counts_df.iterrows():
                        sample_id = get_sample_id(session, j, project_id)
                        for cat in counts_df.columns.values.tolist():
                            if int(j_row[cat]) > 0:
                                d.append(
                                    {
                                        'sample_id': sample_id,
                                        'seq_type_id': seq_type_id,
                                        'cat_id': cat_to_id_map[cat_type][cat],
                                        'value': int(j_row[cat])
                                    }
                                )
        engine.execute(
            MutationCount.__table__.insert(),
            d
        )
        print(f'* Filled mut counts ({len(d)}) for project {i_row[META_COL_PROJ]}')
    return

if __name__ == "__main__":
    data_df = pd.read_csv(META_DATA_FILE, sep='\t')

    
    data_df = data_df.head() # TODO: remove


    sigs_df = pd.read_csv(META_SIGS_FILE, sep='\t')
    pathways_df = pd.read_csv(META_PATHWAYS_FILE, sep='\t')
    tricounts_df = pd.read_csv(META_TRICOUNTS_FILE, sep='\t')

    # Connect to the db
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


    # Get the session
    Session = sessionmaker(bind=connection)
    session = Session()

    # Clear all tables that are about to be filled
    # DO NOT CLEAR SESSION, WORKFLOW, OR USER TABLES
    to_drop = [
        PathwayGene,
        Pathway,
        PathwayGroup,
        GeneExpressionValue,
        GeneMutationValue,
        GeneMutationClass,
        GeneCopyNumberValue,
        Gene,
        ClinicalValue,
        ClinicalVariableValue,
        ClinicalVariable,
        SignatureCategory,
        Signature,
        MutationCount,
        MutationCategory,
        MutationCategoryType,
        MutationType,
        Sample,
        ProjectOncotreeMapping,
        Project,
        ProjectSource,
        TrinucleotideCount,
        SequencingType,
        SignatureGroup
    ]
    for t in to_drop:
        try:
            t.__table__.drop(engine, checkfirst=True)
        except Exception as e:
            print(e)
    print('* Successfully dropped old tables')

    Base.metadata.create_all(bind=engine)
    print('* Successfully created new tables')
    
    # Fill tables
    project_sources = create_project_sources(session, data_df)
    session.add_all(project_sources)
    session.commit()
    print('* Filled project source table')

    seq_types = create_seq_types(session, data_df)
    session.add_all(seq_types)
    session.commit()
    print('* Filled seq type table')

    projects = create_projects(session, data_df)
    session.add_all(projects)
    session.commit()
    print('* Filled project table')

    samples = create_samples_and_commit(engine, session, data_df)
    print('* Filled sample table')

    mut_types = create_mut_types(session)
    session.add_all(mut_types)
    session.commit()
    print('* Filled mut type table')

    cat_types = create_cat_types(session)
    session.add_all(cat_types)
    session.commit()
    print('* Filled cat type table')

    cats = create_cats(session, sigs_df)
    session.add_all(cats)
    session.commit()
    print('* Filled cat table')

    sig_groups = create_sig_groups(session, sigs_df)
    session.add_all(sig_groups)
    session.commit()
    print('* Filled sig group table')

    sigs = create_sigs(session, sigs_df)
    session.add_all(sigs)
    session.commit()
    print('* Filled sig table')

    sig_cats = create_sig_cats_and_commit(engine, session, sigs_df)
    print('* Filled sig cat table')

    mut_counts = create_mut_counts_and_commit(engine, session, data_df)
    print('* Filled mut counts table')

    print('* Done filling')