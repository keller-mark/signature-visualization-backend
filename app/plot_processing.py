import pandas as pd
import numpy as np
import os
import io
from yaml import load
from yaml import Loader
from web_constants import *
from signatures import Signatures

HAS_CLINICAL = "has_clinical"
HAS_SSM = "has_ssm"
HAS_COUNTS = "has_counts"

class PlotProcessing():

  @staticmethod
  def project_metadata(filepaths = True):
    meta_df = pd.read_csv(DATA_META_FILE, sep='\t', index_col=0)
    meta_df[HAS_CLINICAL] = pd.notnull(meta_df["clinical_path"])
    meta_df[HAS_SSM] = (meta_df["extended_sbs_path"].notnull() & meta_df["extended_dbs_path"].notnull() & meta_df["extended_indel_path"].notnull())
    meta_df[HAS_COUNTS] = (meta_df["counts_sbs_path"].notnull() & meta_df["counts_dbs_path"].notnull() & meta_df["counts_indel_path"])
    meta_df = meta_df.fillna(value="")
    if not filepaths:
      meta_df = meta_df.drop(columns=[
        'clinical_path', 
        'extended_sbs_path', 
        'counts_sbs_path', 
        'extended_dbs_path', 
        'counts_dbs_path', 
        'extended_indel_path', 
        'counts_indel_path'
      ])
    meta_df = meta_df.transpose()
    return meta_df.to_dict()
  
  @staticmethod
  def pd_fetch_tsv(s3_key, **kwargs):
    filepath = os.path.join(OBJ_DIR, s3_key)
    return pd.read_csv(filepath, sep='\t', **kwargs)

  @staticmethod
  def pd_as_file(df, index_val=True):
    output = io.StringIO()
    df.to_csv(output, index=index_val)
    return output.getvalue()


  @staticmethod
  def signature(name):
    signatures = Signatures(SIGS_FILE, SIGS_META_FILE)
    return signatures.get_sig_as_dict(name)

  @staticmethod
  def sigs_per_cancer_type():
    if not os.path.isfile(SIGS_PER_CANCER_TYPE_FILE):
      return None
    with open(SIGS_PER_CANCER_TYPE_FILE) as data_file:    
      active_sigs = load(data_file, Loader=Loader)
    return active_sigs

  @staticmethod
  def data_listing_json():
    signatures = Signatures(SIGS_FILE, SIGS_META_FILE)
    return {
      "sources": PlotProcessing.project_metadata(filepaths = False),
      "sigs": signatures.get_metadata(),
      "sig_presets": PlotProcessing.sigs_per_cancer_type()
    }
  
  
  @staticmethod
  def chromosome_bands():
    df = pd.read_csv(CHROMOSOME_BANDS_FILE, sep='\t')

    return PlotProcessing.pd_as_file(df, index_val=False)
  
