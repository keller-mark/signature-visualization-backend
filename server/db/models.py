import os
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Float, Boolean, DateTime
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'auth'
    __table_args__ = { 'extend_existing': True }

    id = Column(Integer, primary_key=True)
    token = Column(String(length=255))
    created = Column(DateTime, default=datetime.now)


class Workflow(Base):
    __tablename__ = 'workflow'
    __table_args__ = { 'extend_existing': True }

    id = Column(Integer, primary_key=True)
    slug = Column(String(length=255))
    data = Column(Text)


class Session(Base):
    __tablename__ = 'session'
    __table_args__ = { 'extend_existing': True }

    id = Column(Integer, primary_key=True)
    slug = Column(String(length=255))
    data = Column(Text)


class MutationType(Base):
    __tablename__ = 'mut_type'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255))

    category_types = relationship("MutationCategoryType")


class MutationCategoryType(Base):
    __tablename__ = 'mut_cat_type'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255))
    mut_type_id = Column(Integer, ForeignKey('mut_type.id'))

    categories = relationship("MutationCategory")
    signatures = relationship("Signature")


class MutationCategory(Base):
    __tablename__ = 'mut_cat'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255))
    cat_type_id = Column(Integer, ForeignKey('mut_cat_type.id'))


class SignatureGroup(Base):
    __tablename__ = 'sig_group'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255))
    publication = Column(String(length=255))

    signatures = relationship("Signature")


class Signature(Base):
    __tablename__ = 'sig'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255))
    index = Column(Integer)
    description = Column(Text)
    cat_type_id = Column(Integer, ForeignKey('mut_cat_type.id'))
    group_id = Column(Integer, ForeignKey('sig_group.id'))

    categories = relationship("SignatureCategory")


class SignatureCategory(Base):
    __tablename__ = 'sig_cat'

    id = Column(Integer, primary_key=True)
    sig_id = Column(Integer, ForeignKey('sig.id'))
    cat_id = Column(Integer, ForeignKey('mut_cat.id'))
    value = Column(Float)


class ProjectSource(Base):
    __tablename__ = 'project_source'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255))

    projects = relationship("Project")


class SequencingType(Base):
    __tablename__ = 'seq_type'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255))

    projects = relationship("Project")


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255))
    name_nice = Column(String(length=255))
    seq_type_id = Column(Integer, ForeignKey('seq_type.id'))
    source_id = Column(Integer, ForeignKey('project_source.id'))
    oncotree_code = Column(String(length=255))

    samples = relationship("Sample")


class Sample(Base):
    __tablename__ = 'sample'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    sample_name = Column(String(length=255))
    patient_name = Column(String(length=255))

    mut_counts = relationship("MutationCount")


class MutationCount(Base):
    __tablename__ = 'mut_count'

    id = Column(Integer, primary_key=True)
    sample_id = Column(Integer, ForeignKey('sample.id'))
    cat_id = Column(Integer, ForeignKey('mut_cat.id'))
    seq_type_id = Column(Integer, ForeignKey('seq_type.id'))
    value = Column(Integer)


class ClinicalVariable(Base):
    __tablename__ = 'clinical_var'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(length=255))
    scale_type = Column(String(length=255))
    extent = Column(String(length=255))

    values = relationship("ClinicalVariableValue")


class ClinicalVariableValue(Base):
    __tablename__ = 'clinical_var_val'

    # all possible values a clinical variable can take
    
    id = Column(Integer, primary_key=True)
    variable_id = Column(Integer, ForeignKey('clinical_var.id'))
    value = Column(String(length=255))


class ClinicalValue(Base):
    __tablename__ = 'clinical_val'
    
    # a particular value for a particular sample

    id = Column(Integer, primary_key=True)
    sample_id = Column(Integer, ForeignKey('sample.id'))
    variable_id = Column(Integer, ForeignKey('clinical_var.id'))
    value = Column(String(length=255))


class Gene(Base):
    __tablename__ = 'gene'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255))


class GeneExpressionValue(Base):
    __tablename__ = 'gene_exp_val'

    id = Column(Integer, primary_key=True)
    gene_id = Column(Integer, ForeignKey('gene.id'))
    sample_id = Column(Integer, ForeignKey('sample.id'))
    zscore = Column(Float)


class GeneMutationClass(Base):
    __tablename__ = 'gene_mut_class'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255))


class GeneMutationValue(Base):
    __tablename__ = 'gene_mut_val'

    id = Column(Integer, primary_key=True)
    gene_id = Column(Integer, ForeignKey('gene.id'))
    sample_id = Column(Integer, ForeignKey('sample.id'))
    mut_class_id = Column(Integer, ForeignKey('gene_mut_class.id'))


class GeneCopyNumberValue(Base):
    __tablename__ = 'gene_cna_val'

    id = Column(Integer, primary_key=True)
    gene_id = Column(Integer, ForeignKey('gene.id'))
    sample_id = Column(Integer, ForeignKey('sample.id'))
    copy_number = Column(Integer)


class PathwayGroup(Base):
    __tablename__ = 'pathway_group'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255))
    publication = Column(String(length=255))

    pathways = relationship("Pathway")


class Pathway(Base):
    __tablename__ = 'pathway'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255))
    group_id = Column(Integer, ForeignKey('pathway_group.id'))

    genes = relationship("PathwayGene")


class PathwayGene(Base):
    __tablename__ = 'pathway_gene'

    id = Column(Integer, primary_key=True)
    gene_id = Column(Integer, ForeignKey('gene.id'))
    pathway_id = Column(Integer, ForeignKey('pathway.id'))
    is_core = Column(Boolean)


class TrinucleotideCount(Base):
    __tablename__ = 'tri_count'

    id = Column(Integer, primary_key=True)
    trinucleotide = Column(String(length=255))
    seq_type_id = Column(Integer, ForeignKey('seq_type.id'))
    value = Column(Integer)


class ProjectOncotreeMapping(Base):
    __tablename__ = 'proj_oncotree_map'

    # mapping of projects to signature cancer types by Oncotree codes

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    sig_group_id = Column(Integer, ForeignKey('sig_group.id'))
    oncotree_code = Column(String(length=255))