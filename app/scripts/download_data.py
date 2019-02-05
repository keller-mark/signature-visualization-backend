import pandas as pd
import subprocess
import os
import sys
import json
import string

from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, Integer, String, Text

# Load our modules
this_file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.normpath(this_file_path + '/../'))
from web_constants import *
from oncotree import *

OBJ_DIR = './obj' if bool(os.environ.get("DEBUG", '')) else '/obj'

META_DATA_FILE = os.path.join(OBJ_DIR, META_DATA_FILENAME)
META_SIGS_FILE = os.path.join(OBJ_DIR, META_SIGS_FILENAME)
META_PATHWAYS_FILE = os.path.join(OBJ_DIR, META_PATHWAYS_FILENAME)
META_FEATURED_FILE = os.path.join(OBJ_DIR, META_FEATURED_FILENAME)
META_TRICOUNTS_FILE = os.path.join(OBJ_DIR, META_TRICOUNTS_FILENAME)

GENES_AGG_FILE = os.path.join(OBJ_DIR, GENES_AGG_FILENAME)
SAMPLES_AGG_FILE = os.path.join(OBJ_DIR, SAMPLES_AGG_FILENAME)
ONCOTREE_FILE = os.path.join(OBJ_DIR, ONCOTREE_FILENAME)
PROJ_TO_SIGS_FILE = os.path.join(OBJ_DIR, PROJ_TO_SIGS_FILENAME)

OBJ_STORE_URL = "https://mutation-signature-explorer.obj.umiacs.umd.edu/"
ONCOTREE_URL = "http://oncotree.mskcc.org/api/tumorTypes/tree?version=oncotree_2018_11_01"

def read_tsv(csv_file_path, **kwargs):
  return pd.read_csv(os.path.join(OBJ_DIR, csv_file_path), sep='\t', **kwargs)

def to_tsv(df, csv_file_path, **kwargs):
  df.to_csv(os.path.join(OBJ_DIR, csv_file_path), sep='\t', **kwargs)

def download_files(file_list):
  for file_path in file_list:
    local_file_path = os.path.join(OBJ_DIR, file_path)
    remote_file_url = OBJ_STORE_URL + file_path
    if not os.path.isfile(local_file_path):
      print('* Downloading ' + local_file_path)
      subprocess.run(['curl', remote_file_url, '--create-dirs', '-o', local_file_path])
    else:
      print('* Not downloading ' + local_file_path)

def create_genes_agg_files():
  print('* Creating genes aggregate files')
  alphabet = string.ascii_uppercase
  for letter in alphabet:
    genes_agg_df = pd.DataFrame(index=[], columns=[META_COL_PROJ, GENE_SYMBOL, "count"])
    genes_agg_df.to_csv(GENES_AGG_FILE.format(letter=letter), sep='\t', index=False)

def create_samples_agg_file():
  print('* Creating samples aggregate file')
  samples_agg_df = pd.DataFrame(index=[], columns=[META_COL_PROJ, "count"])
  samples_agg_df.to_csv(SAMPLES_AGG_FILE, sep='\t', index=False)

def clean_data_files(data_row):
  print('* Appending to samples aggregate file')
  samples_agg_df = pd.read_csv(SAMPLES_AGG_FILE, sep='\t')
  # join all counts dfs
  counts_df = pd.DataFrame(index=[], data=[])
  for cat_type_count_path in META_COL_PATH_MUTS_COUNTS_LIST:
    if pd.notnull(data_row[cat_type_count_path]):
      cat_type_counts_df = read_tsv(data_row[cat_type_count_path], index_col=0)
      counts_df = counts_df.join(cat_type_counts_df, how='outer')
  
  counts_df = counts_df.fillna(value=0)
  counts_df = counts_df.loc[~(counts_df==0).all(axis=1)]
  # compute the number of samples and append a row to the samples agg dataframe
  num_samples = len(list(counts_df.index.values))
  samples_agg_df = samples_agg_df.append({META_COL_PROJ: data_row[META_COL_PROJ], "count": num_samples}, ignore_index=True)
  samples_agg_df.to_csv(SAMPLES_AGG_FILE, sep='\t', index=False)

  if pd.notnull(data_row[META_COL_PATH_GENES]):
    print('* Appending to genes aggregate files')
    genes_df = read_tsv(data_row[META_COL_PATH_GENES])
    genes_df[META_COL_PROJ] = data_row[META_COL_PROJ]
    genes_df = genes_df.groupby([META_COL_PROJ, GENE_SYMBOL]).size().reset_index(name='count')

    alphabet = string.ascii_uppercase
    for letter in alphabet:
      genes_agg_df = pd.read_csv(GENES_AGG_FILE.format(letter=letter), sep='\t')
      genes_df_by_letter = genes_df.loc[genes_df[GENE_SYMBOL].str.startswith(letter)]
      if genes_df_by_letter.shape[0] > 0:
        genes_agg_df = genes_agg_df.append(genes_df_by_letter, ignore_index=True)
        genes_agg_df.to_csv(GENES_AGG_FILE.format(letter=letter), sep='\t', index=False)

def download_oncotree():
  if not os.path.isfile(ONCOTREE_FILE):
    print('* Downloading Oncotree file')
    subprocess.run(['curl', ONCOTREE_URL, '--create-dirs', '-o', ONCOTREE_FILE])
  else:
    print('* Not downloading Oncotree file')


def load_oncotree():
  with open(ONCOTREE_FILE) as f:
    tree_json = json.load(f)
    return OncoTree(tree_json)

def create_proj_to_sigs_mapping(data_df, sigs_df):
  print('* Mapping projects to signature cancer types by Oncotree codes')
  tree = load_oncotree()
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
              match_df = match_df.append({
                META_COL_PROJ: data_row[META_COL_PROJ],
                META_COL_SIG_GROUP: sig_group_row[META_COL_SIG_GROUP],
                META_COL_ONCOTREE_CODE: sig_group_parent_node.code
              }, ignore_index=True)
  match_df.to_csv(PROJ_TO_SIGS_FILE, index=False, sep='\t')

def create_sharing_table():
  try:
    engine = create_engine('mysql://explosig:explosig@db:3306/explosig')
    connection = engine.connect()
    metadata = MetaData(engine)
    table = Table('sharing', metadata, Column('id', Integer(), primary_key=True), Column('slug', String(length=255)), Column('data', Text()), extend_existing=True)
    metadata.create_all()
    print('* Successfully connected to database and created sharing table')
  except:
    print('* Unable to connect to database')

if __name__ == "__main__":
  data_df = pd.read_csv(META_DATA_FILE, sep='\t')
  sigs_df = pd.read_csv(META_SIGS_FILE, sep='\t')
  pathways_df = pd.read_csv(META_PATHWAYS_FILE, sep='\t')
  tricounts_df = pd.read_csv(META_TRICOUNTS_FILE, sep='\t')

  create_genes_agg_files()
  create_samples_agg_file()

  file_list = []
  for file_column in META_DATA_FILE_COLS:
    file_list += data_df[file_column].dropna().tolist()
  for file_column in META_SIGS_FILE_COLS:
    file_list += sigs_df[file_column].dropna().tolist()
  for file_column in META_PATHWAYS_FILE_COLS:
    file_list += pathways_df[file_column].dropna().tolist()
  for file_column in META_TRICOUNTS_FILE_COLS:
    file_list += tricounts_df[file_column].dropna().tolist()
  download_files(file_list)

  for index, data_row in data_df.iterrows():
    clean_data_files(data_row)
  
  download_oncotree()
  create_proj_to_sigs_mapping(data_df, sigs_df)

  create_sharing_table()
  
  print('* Done')