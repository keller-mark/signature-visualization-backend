import pandas as pd
import numpy as np
import subprocess
import os
import sys
import json
import string

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

# Load our modules
this_file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.normpath(this_file_path + '/../'))
from web_constants import *
from oncotree import *

from db import db_connect
from db_models import (
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
    ProjectOncotreeMapping,
    SignatureOncotreeMapping
)


OBJ_DIR = '../../obj' # TODO: remove
#OBJ_DIR = '/obj'

META_DATA_FILE = os.path.join(OBJ_DIR, META_DATA_FILENAME)
META_SIGS_FILE = os.path.join(OBJ_DIR, META_SIGS_FILENAME)
META_PATHWAYS_FILE = os.path.join(OBJ_DIR, META_PATHWAYS_FILENAME)
META_FEATURED_FILE = os.path.join(OBJ_DIR, META_FEATURED_FILENAME)
META_CLINICAL_FILE = os.path.join(OBJ_DIR, META_CLINICAL_FILENAME)
META_TRICOUNTS_FILE = os.path.join(OBJ_DIR, META_TRICOUNTS_FILENAME)

ONCOTREE_FILE = os.path.join(OBJ_DIR, ONCOTREE_FILENAME)


# Hard-coded mutation and category types for now.
# In the future, a metadata file could allow these to be generalized.
CAT_TYPE_MAP = {
  'SBS': ['SBS_96'],
  'DBS': ['DBS_78'],
  'INDEL': ['INDEL_Alexandrov2018_83']
}

# Utility functions
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


"""
=====================================
Projects
=====================================
"""

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

def try_get_seq_type_id(session, name):
    try:
        return get_seq_type_id(session, name)
    except NoResultFound:
        seq_type = SequencingType(name=name)
        session.add(seq_type)
        session.commit()
        return seq_type.id

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


"""
=====================================
Samples
=====================================
"""

def create_samples_and_commit(engine, session, data_df):
    for i, i_row in data_df.iterrows():
        d = []
        project_id = get_project_id(session, i_row[META_COL_PROJ])
        samples_df = read_tsv(i_row[META_COL_PATH_SAMPLES])

        counts_df = pd.DataFrame(index=[], data=[])
        for mut_type, cat_types in CAT_TYPE_MAP.items():
            for cat_type in cat_types:
                if pd.notnull(i_row[META_COL_PATH_MUTS_COUNTS.format(cat_type=cat_type)]):
                    cat_type_counts_df = read_tsv(i_row[META_COL_PATH_MUTS_COUNTS.format(cat_type=cat_type)], index_col=0)
                    counts_df = counts_df.join(cat_type_counts_df, how='outer')
        counts_df = counts_df.fillna(value=0)
        counts_df = counts_df.loc[~(counts_df==0).all(axis=1)]
        counts_sum_df = counts_df.sum(axis=1).to_frame().rename(columns={0:'sum'})

        # Only use one sample per patient, the one with the most mutations
        samples_sum_df = samples_df.set_index(SAMPLE).join(counts_sum_df, how='right')
        samples_sum_df = samples_sum_df.sort_values(by=['sum'], ascending=False)
        samples_sum_df = samples_sum_df.drop_duplicates(subset=[PATIENT], keep='first')

        unique_patient_samples = samples_sum_df.index.values.tolist()

        for j, j_row in samples_df.iterrows():
            # Only use those samples that actually have mutation counts
            if j_row[SAMPLE] in unique_patient_samples:
                d.append(
                    {
                        'project_id': project_id,
                        'sample_name': j_row[SAMPLE],
                        'patient_name': j_row[PATIENT]
                    }
                )
        engine.execute(Sample.__table__.insert(), d)
        print(f'* Filled samples ({len(d)}) for project {i_row[META_COL_PROJ]}')
    return    

def get_sample_id(session, name, project_id):
    sample = session.query(Sample).filter(
        and_(
            Sample.project_id == project_id,
            Sample.sample_name == name
        )
    ).one_or_none()
    if sample != None:
        return sample.id
    
    if name.startswith('TCGA'):
        # May be a short cBioPortal-style sample ID
        sample = session.query(Sample).filter(
            and_(
                Sample.project_id == project_id,
                Sample.sample_name.startswith(name)
            )
        ).one_or_none()
        if sample != None:
            return sample.id

    return None

def get_sample_id_by_patient_name(session, name, project_id):
    sample = session.query(Sample).filter(
        and_(
            Sample.project_id == project_id,
            Sample.patient_name == name
        )
    ).one_or_none()
    if sample != None:
        return sample.id
    return None

def generate_sample_to_id_map_by_project(session, project_id):
    sample_to_id_map = {}
    samples = session.query(Sample).filter(Sample.project_id == project_id).all()
    for sample in samples:
        sample_to_id_map[sample.sample_name] = sample.id
        if sample.sample_name.startswith('TCGA'):
            # Handle short cBioPortal-style sample IDs
            sample_to_id_map[sample.sample_name[:15]] = sample.id
    return sample_to_id_map


"""
=====================================
Mutation types and categories
=====================================
"""

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
    # TODO: generalize by querying db for all categories first
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


"""
=====================================
Signature data
=====================================
"""

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


"""
=====================================
Counts data
=====================================
"""

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
                        if sample_id != None:
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
        engine.execute(MutationCount.__table__.insert(), d)
        print(f'* Filled mut counts ({len(d)}) for project {i_row[META_COL_PROJ]}')
    return


"""
=====================================
Clinical data
=====================================
"""

def create_clinical_vars(session, clinical_df):
    d = []
    unique_clinical_df = clinical_df.drop_duplicates(subset=[META_COL_CLINICAL_COL])
    for i, i_row in unique_clinical_df.iterrows():
        d.append(
            ClinicalVariable(
                name=i_row[META_COL_CLINICAL_COL],
                scale_type=i_row[META_COL_CLINICAL_SCALE_TYPE],
                extent=anull(i_row[META_COL_CLINICAL_EXTENT])
            )
        )
    return d

def get_clinical_var_id(session, name):
    return session.query(ClinicalVariable).filter(
        ClinicalVariable.name == name
    ).one().id

def create_clinical_var_values(session, clinical_df):
    d = []
    for i, i_row in clinical_df.iterrows():
        if anull(i_row[META_COL_CLINICAL_EXTENT]) == None:
            clinical_var_id = get_clinical_var_id(session, i_row[META_COL_CLINICAL_COL])
            d.append(
                ClinicalVariableValue(
                    clinical_var_id=clinical_var_id,
                    value=i_row[META_COL_CLINICAL_VALUE]
                )
            )
    return d

def generate_clinical_var_to_id_map(session):
    var_to_id_map = {}
    clinical_vars = session.query(ClinicalVariable).all()
    for clinical_var in clinical_vars:
        var_to_id_map[clinical_var.name] = clinical_var.id
    return var_to_id_map

def create_clinical_values_and_commit(engine, session, data_df):
    var_to_id_map = generate_clinical_var_to_id_map(session)

    for i, i_row in data_df.iterrows():
        d = []
        project_id = get_project_id(session, i_row[META_COL_PROJ])
        if anull(i_row[META_COL_PATH_CLINICAL]) != None:
            clinical_df = read_tsv(i_row[META_COL_PATH_CLINICAL], index_col=0)
            for clinical_var, clinical_var_id in var_to_id_map.items():
                if clinical_var in clinical_df.columns.values.tolist():
                    for j, j_row in clinical_df.iterrows():
                        sample_id = get_sample_id_by_patient_name(session, j, project_id)
                        if sample_id != None and anull(j_row[clinical_var]) != None:
                            d.append(
                                {
                                    'sample_id': sample_id,
                                    'clinical_var_id': clinical_var_id,
                                    'value': j_row[clinical_var]
                                }
                            )
        engine.execute(
            ClinicalValue.__table__.insert(),
            d
        )
        print(f'* Filled clinical values ({len(d)}) for project {i_row[META_COL_PROJ]}')
    return


"""
=====================================
Genes data
=====================================
"""

def create_genes_and_commit(engine, session, data_df):
    gene_names = set()
    gene_mut_classes = set()
    for i, i_row in data_df.iterrows():
        if anull(i_row[META_COL_PATH_GENE_MUT]) != None:
            genes_df = read_tsv(i_row[META_COL_PATH_GENE_MUT])
            gene_names = gene_names.union(list(genes_df[GENE_SYMBOL].unique()))
            mut_classes = list(genes_df[MUT_CLASS].unique())
            mut_classes = [ str(mc).split(",") for mc in mut_classes if anull(mc) != None ]
            if len(mut_classes) > 0:
                gene_mut_classes = gene_mut_classes.union(*mut_classes)
        print(f'* Updated genes ({len(gene_names)}) after project {i_row[META_COL_PROJ]}')
    
    engine.execute(
        Gene.__table__.insert(),
        [ { 'name': name } for name in gene_names ]
    )
    engine.execute(
        GeneMutationClass.__table__.insert(),
        [ { 'name': name } for name in gene_mut_classes ]
    )
    return

def get_gene_id(session, name):
    return session.query(Gene).filter(
        Gene.name == name
    ).one().id

def get_gene_mut_class_id(session, name):
    return session.query(GeneMutationClass).filter(
        GeneMutationClass.name == name
    ).one().id

def generate_gene_to_id_map(session):
    gene_to_id_map = {}
    genes = session.query(Gene).all()
    for gene in genes:
        gene_to_id_map[gene.name] = gene.id
    return gene_to_id_map

def generate_gene_mut_class_to_id_map(session):
    class_to_id_map = {}
    mut_classes = session.query(GeneMutationClass).all()
    for mut_class in mut_classes:
        class_to_id_map[mut_class.name] = mut_class.id
    return class_to_id_map

def create_gene_mut_values_and_commit(engine, session, data_df):
    n_rows = 0
    gene_to_id_map = generate_gene_to_id_map(session)
    class_to_id_map = generate_gene_mut_class_to_id_map(session)

    for i, i_row in data_df.iterrows():
        project_id = get_project_id(session, i_row[META_COL_PROJ])
        sample_to_id_map = generate_sample_to_id_map_by_project(session, project_id)
        if anull(i_row[META_COL_PATH_GENE_MUT]) != None:
            d = []
            genes_df = read_tsv(i_row[META_COL_PATH_GENE_MUT])
            for j, j_row in genes_df.iterrows():
                try:
                    sample_id = sample_to_id_map[j_row[SAMPLE]]
                except KeyError:
                    sample_id = None
                if sample_id != None and anull(j_row[MUT_CLASS]) != None:
                    mut_classes = j_row[MUT_CLASS].split(",")
                    for mut_class in mut_classes:
                        d.append(
                            {
                                'sample_id': sample_id,
                                'gene_id': gene_to_id_map[j_row[GENE_SYMBOL]],
                                'mut_class_id': class_to_id_map[mut_class]
                            }
                        )
                        if len(d) >= 100000:
                            engine.execute(GeneMutationValue.__table__.insert(), d)
                            n_rows += len(d)
                            d = []
            engine.execute(GeneMutationValue.__table__.insert(), d)
            n_rows += len(d)
            print(f'* Filled gene mutation values ({n_rows}) for project {i_row[META_COL_PROJ]}')
    return

def try_gene_id_map(session, id_map, name):
    try:
        return id_map[name], id_map
    except KeyError:
        gene = Gene(name=name)
        session.add(gene)
        session.commit()
        id_map[name] = gene.id
        return id_map[name], id_map

def create_gene_exp_values_and_commit(engine, session, data_df):
    n_rows = 0
    gene_to_id_map = generate_gene_to_id_map(session)
    class_to_id_map = generate_gene_mut_class_to_id_map(session)

    for i, i_row in data_df.iterrows():
        project_id = get_project_id(session, i_row[META_COL_PROJ])
        sample_to_id_map = generate_sample_to_id_map_by_project(session, project_id)
        if anull(i_row[META_COL_PATH_GENE_EXP]) != None:
            d = []
            genes_df = read_tsv(i_row[META_COL_PATH_GENE_EXP])
            for j, j_row in genes_df.iterrows():
                try:
                    sample_id = sample_to_id_map[j_row[SAMPLE]]
                except KeyError:
                    sample_id = None
                if sample_id != None:
                    gene_id, gene_to_id_map = try_gene_id_map(session, gene_to_id_map, j_row[GENE_SYMBOL])
                    d.append(
                        {
                            'sample_id': sample_id,
                            'gene_id': gene_id,
                            'zscore': float(j_row[GENE_EXPRESSION_RNA_SEQ_MRNA_Z])
                        }
                    )

                    if len(d) >= 100000:
                        engine.execute(GeneExpressionValue.__table__.insert(), d)
                        n_rows += len(d)
                        d = []
                
            engine.execute(GeneExpressionValue.__table__.insert(), d)
            n_rows += len(d)
            print(f'* Filled gene expression values ({n_rows}) for project {i_row[META_COL_PROJ]}')
    return

def create_gene_cna_values_and_commit(engine, session, data_df):
    n_rows = 0
    gene_to_id_map = generate_gene_to_id_map(session)
    class_to_id_map = generate_gene_mut_class_to_id_map(session)

    for i, i_row in data_df.iterrows():
        project_id = get_project_id(session, i_row[META_COL_PROJ])
        sample_to_id_map = generate_sample_to_id_map_by_project(session, project_id)
        if anull(i_row[META_COL_PATH_GENE_CNA]) != None:
            d = []
            genes_df = read_tsv(i_row[META_COL_PATH_GENE_CNA], index_col=0)
            genes_df = genes_df.transpose()
            genes_df.index = genes_df.index.rename(SAMPLE)
            genes_df = genes_df.reset_index()
            # wide -> narrow
            genes_df = genes_df.melt(id_vars=[SAMPLE], var_name=GENE_SYMBOL, value_name='copy_number')

            for j, j_row in genes_df.iterrows():
                if int(j_row['copy_number']) != 0:
                    try:
                        sample_id = sample_to_id_map[j_row[SAMPLE]]
                    except KeyError:
                        sample_id = None
                    if sample_id != None:
                        gene_id, gene_to_id_map = try_gene_id_map(session, gene_to_id_map, j_row[GENE_SYMBOL])
                        d.append(
                            {
                                'sample_id': sample_id,
                                'gene_id': gene_id,
                                'copy_number': int(j_row['copy_number'])
                            }
                        )
                    
                        if len(d) >= 100000:
                            engine.execute(GeneCopyNumberValue.__table__.insert(), d)
                            n_rows += len(d)
                            d = []
            engine.execute(GeneCopyNumberValue.__table__.insert(), d)
            n_rows += len(d)
            print(f'* Filled gene copy number values ({n_rows}) for project {i_row[META_COL_PROJ]}')
    return


"""
=====================================
Pathways data
=====================================
"""

def create_pathway_groups(session, pathways_df):
    d = []
    for i, i_row in pathways_df.iterrows():
        d.append(
            PathwayGroup(
                name=i_row[META_COL_PATHWAYS_GROUP],
                publication=i_row[META_COL_PUBLICATION]
            )
        )
    return d

def get_pathway_group_id(session, name):
    return session.query(PathwayGroup).filter(
        PathwayGroup.name == name
    ).one().id

def create_pathways(session, pathway_groups_df):
    d = []
    for i, i_row in pathway_groups_df.iterrows():
        group_id = get_pathway_group_id(session, i_row[META_COL_PATHWAYS_GROUP])
        pathways_df = read_tsv(i_row[META_COL_PATH_PATHWAYS])
        pathways = pathways_df[PATHWAY].unique()
        d += [ Pathway(name=name, group_id=group_id) for name in pathways ]
    return d

def get_pathway_id(session, name, group_id):
    return session.query(Pathway).filter(
        and_(
            Pathway.group_id == group_id,
            Pathway.name == name
        )
    ).one().id

def create_pathway_genes(session, pathway_groups_df):
    gene_to_id_map = generate_gene_to_id_map(session)

    d = []
    for i, i_row in pathway_groups_df.iterrows():
        group_id = get_pathway_group_id(session, i_row[META_COL_PATHWAYS_GROUP])
        pathways_df = read_tsv(i_row[META_COL_PATH_PATHWAYS])
        for j, j_row in pathways_df.iterrows():
            pathway_id = get_pathway_id(session, j_row[PATHWAY], group_id)
            gene_id, gene_to_id_map = try_gene_id_map(session, gene_to_id_map, j_row[GENE_SYMBOL])
            d.append(
                PathwayGene(
                    gene_id=gene_id,
                    pathway_id=pathway_id,
                    is_core=j_row[PATHWAY_CORE]
                )
            )
    return d


"""
=====================================
Trinucleotide count data
=====================================
"""

def create_tricounts(session, tricounts_df):
    d = []
    for i, i_row in tricounts_df.iterrows():
        method_df = read_tsv(i_row[META_COL_PATH_TRICOUNTS])
        seq_type_id = try_get_seq_type_id(session, i_row[META_COL_TRICOUNTS_METHOD])
        for j, j_row in method_df.iterrows():
            d.append(
                TrinucleotideCount(
                    trinucleotide=j_row[TRINUCLEOTIDE],
                    seq_type_id=seq_type_id,
                    value=j_row[TRINUCLEOTIDE_COUNT]
                )
            )
    return d


"""
=====================================
Project-Oncotree mappings
=====================================
"""

def create_proj_oncotree_mappings(session, data_df, sigs_df):
    d = []
    tree = load_oncotree()
    for i, i_row in data_df.iterrows():
        if anull(i_row[META_COL_ONCOTREE_CODE]) != None:
            proj_node = tree.find_node(i_row[META_COL_ONCOTREE_CODE])
            if proj_node is not None:
                project_id = get_project_id(session, i_row[META_COL_PROJ])
                for j, j_row in sigs_df.iterrows():
                    if anull(j_row[META_COL_PATH_SIGS_CANCER_TYPE_MAP]) != None:
                        sig_group_id = get_sig_group_id(session, j_row[META_COL_SIG_GROUP])
                        sig_group_cancer_type_map_df = read_tsv(j_row[META_COL_PATH_SIGS_CANCER_TYPE_MAP])
                        cancer_type_map_codes = list(sig_group_cancer_type_map_df[META_COL_ONCOTREE_CODE].dropna().unique())
                        sig_group_parent_node = proj_node.find_closest_parent(cancer_type_map_codes)
                        if sig_group_parent_node is not None:
                            d.append(
                                ProjectOncotreeMapping(
                                    project_id=project_id,
                                    sig_group_id=sig_group_id,
                                    oncotree_code=sig_group_parent_node.code
                                )
                            )
    return d


"""
=====================================
Signature-Oncotree mappings
=====================================
"""

def create_sig_oncotree_mappings(session, sigs_df):
    d = []
    for i, i_row in sigs_df.iterrows():
        if anull(i_row[META_COL_PATH_SIGS_CANCER_TYPE_MAP]) != None:
            sig_group_id = get_sig_group_id(session, i_row[META_COL_SIG_GROUP])
            cancer_type_map_df = read_tsv(i_row[META_COL_PATH_SIGS_CANCER_TYPE_MAP])
            for j, j_row in cancer_type_map_df.iterrows():
                if anull(j_row[META_COL_ONCOTREE_CODE]) != None:
                    d.append(
                        SignatureOncotreeMapping(
                            sig_id=get_sig_id(session, j_row[META_COL_SIG], sig_group_id),
                            oncotree_code=j_row[META_COL_ONCOTREE_CODE],
                            cancer_type=j_row[META_COL_CANCER_TYPE]
                        )
                    )
    return d



if __name__ == "__main__":
    data_df = pd.read_csv(META_DATA_FILE, sep='\t')
    sigs_df = pd.read_csv(META_SIGS_FILE, sep='\t')
    pathways_df = pd.read_csv(META_PATHWAYS_FILE, sep='\t')
    featured_df = pd.read_csv(META_FEATURED_FILE, sep='\t')
    clinical_df = pd.read_csv(META_CLINICAL_FILE, sep='\t')
    tricounts_df = pd.read_csv(META_TRICOUNTS_FILE, sep='\t')
    

    # Connect to the db
    engine, conn = db_connect()
    print('* Successfully connected to database')


    # Get the session
    Session = sessionmaker(bind=conn)
    session = Session()

    # Clear all tables that are about to be filled
    # DO NOT CLEAR SESSION, WORKFLOW, OR USER TABLES
    to_drop = [
        SignatureOncotreeMapping,
        ProjectOncotreeMapping,
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
    seq_types = create_seq_types(session, data_df)
    session.add_all(seq_types)
    session.commit()
    print('* Filled seq type table')

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
    session.commit()
    print('* Filled sig cat table')

    project_sources = create_project_sources(session, data_df)
    session.add_all(project_sources)
    session.commit()
    print('* Filled project source table')

    projects = create_projects(session, data_df)
    session.add_all(projects)
    session.commit()
    print('* Filled project table')

    samples = create_samples_and_commit(engine, session, data_df)
    session.commit()
    print('* Filled sample table')

    mut_counts = create_mut_counts_and_commit(engine, session, data_df)
    session.commit()
    print('* Filled mut counts table')
    
    clinical_vars = create_clinical_vars(session, clinical_df)
    session.add_all(clinical_vars)
    session.commit()
    print('* Filled clinical vars table')

    clinical_var_values = create_clinical_var_values(session, clinical_df)
    session.add_all(clinical_var_values)
    session.commit()
    print('* Filled clinical var values table')

    clinical_values = create_clinical_values_and_commit(engine, session, data_df)
    session.commit()
    print('* Filled clinical values table')

    genes = create_genes_and_commit(engine, session, data_df)
    session.commit()
    print('* Filled genes table')

    pathway_groups = create_pathway_groups(session, pathways_df)
    session.add_all(pathway_groups)
    session.commit()
    print('* Filled pathway group table')

    pathways = create_pathways(session, pathways_df)
    session.add_all(pathways)
    session.commit()
    print('* Filled pathways table')

    pathway_genes = create_pathway_genes(session, pathways_df)
    session.add_all(pathway_genes)
    session.commit()
    print('* Filled pathway genes table')

    tricounts = create_tricounts(session, tricounts_df)
    session.add_all(tricounts)
    session.commit()
    print('* Filled tricounts table')

    proj_oncotree_mappings = create_proj_oncotree_mappings(session, data_df, sigs_df)
    session.add_all(proj_oncotree_mappings)
    session.commit()
    print('* Filled project oncotree mappings table')

    sig_oncotree_mappings = create_sig_oncotree_mappings(session, sigs_df)
    session.add_all(sig_oncotree_mappings)
    session.commit()
    print('* Filled signature oncotree mappings table')

    gene_mut_values = create_gene_mut_values_and_commit(engine, session, data_df)
    session.commit()
    print('* Filled gene mutation values table')

    exit(0) # TODO: remove

    gene_exp_values = create_gene_exp_values_and_commit(engine, session, data_df)
    session.commit()
    print('* Filled gene expression values table')

    gene_cna_values = create_gene_cna_values_and_commit(engine, session, data_df)
    session.commit()
    print('* Filled gene copy number values table')

    print('* Done filling')