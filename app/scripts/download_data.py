import pandas as pd
import subprocess
import os
import sys

# Load our modules
this_file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.normpath(this_file_path + '/../'))
from web_constants import *

OBJ_DIR = './obj' if bool(os.environ.get("DEBUG", '')) else '/obj'

META_DATA_FILE = os.path.join(OBJ_DIR, META_DATA_FILENAME)
META_SIGS_FILE = os.path.join(OBJ_DIR, META_SIGS_FILENAME)
GENES_AGG_FILE = os.path.join(OBJ_DIR, GENES_AGG_FILENAME)
ONCOTREE_FILE = os.path.join(OBJ_DIR, ONCOTREE_FILENAME)

OBJ_STORE_URL = "https://mutation-signature-explorer.obj.umiacs.umd.edu/"
ONCOTREE_URL = "http://oncotree.mskcc.org/api/tumorTypes/tree?version=oncotree_2018_11_01"

def read_csv(csv_file_path, **kwargs):
  return pd.read_csv(os.path.join(OBJ_DIR, csv_file_path), **kwargs)

def to_csv(df, csv_file_path, **kwargs):
  df.to_csv(os.path.join(OBJ_DIR, csv_file_path), **kwargs)

def download_files(file_list):
  for file_path in file_list:
    local_file_path = os.path.join(OBJ_DIR, file_path)
    remote_file_url = OBJ_STORE_URL + file_path
    if not os.path.isfile(local_file_path):
      print('* Downloading ' + local_file_path)
      subprocess.run(['curl', remote_file_url, '--create-dirs', '-o', local_file_path])
    else:
      print('* Not downloading ' + local_file_path)

def create_genes_agg_file():
  print('* Creating genes aggregate file')
  genes_agg_df = pd.DataFrame(index=[], columns=[META_COL_PROJ, GENE_SYMBOL, "count"])
  genes_agg_df.to_csv(GENES_AGG_FILE, sep='\t', index=False)

def clean_data_files(data_row):
  print('* Cleaning samples file')
  # load data
  samples_df = read_csv(data_row[META_COL_PATH_SAMPLES], sep='\t', usecols=[PATIENT, SAMPLE])
  samples_df = samples_df.set_index(SAMPLE, drop=True)
  if pd.notnull(data_row[META_COL_PATH_CLINICAL]):
    clinical_df = read_csv(data_row[META_COL_PATH_CLINICAL], sep='\t')
    clinical_df = clinical_df.set_index(PATIENT, drop=True)

  # join all counts dfs
  counts_df = pd.DataFrame(index=[], data=[])
  for cat_type_count_path in META_COL_PATH_MUTS_COUNTS_LIST:
    if pd.notnull(data_row[cat_type_count_path]):
      cat_type_counts_df = read_csv(data_row[cat_type_count_path], sep='\t', index_col=0)
      counts_df = counts_df.join(cat_type_counts_df, how='outer')

  # filter and save new samples file
  samples_counts_df = counts_df.join(samples_df, how='left')
  samples_counts_df.index = samples_counts_df.index.rename(SAMPLE)
  samples_counts_df = samples_counts_df.reset_index()
  samples_filtered_df = samples_counts_df[[PATIENT, SAMPLE]]
  to_csv(samples_filtered_df, data_row[META_COL_PATH_SAMPLES], sep='\t', index=False)

  # filter and save new clinical file
  print('* Cleaning clinical file')
  samples_filtered_df = samples_filtered_df.drop_duplicates(subset=[PATIENT])
  samples_filtered_df = samples_filtered_df.set_index(PATIENT, drop=True)
  if pd.notnull(data_row[META_COL_PATH_CLINICAL]):
    clinical_samples_df = samples_filtered_df.join(clinical_df, how='left')
    clinical_filtered_df = clinical_samples_df.drop(columns=[SAMPLE])
    clinical_filtered_df = clinical_filtered_df.reset_index()
    to_csv(clinical_filtered_df, data_row[META_COL_PATH_CLINICAL], sep='\t', index=False)

  if pd.notnull(data_row[META_COL_PATH_GENES]):
    print('* Appending to genes aggregate file')
    genes_agg_df = pd.read_csv(GENES_AGG_FILE, sep='\t')
    genes_df = read_csv(data_row[META_COL_PATH_GENES], sep='\t')
    genes_df[META_COL_PROJ] = data_row[META_COL_PROJ]
    genes_df = genes_df.groupby([META_COL_PROJ, GENE_SYMBOL]).size().reset_index(name='count')
    genes_agg_df = genes_agg_df.append(genes_df, ignore_index=True)
    genes_agg_df.to_csv(GENES_AGG_FILE, sep='\t', index=False)

def download_oncotree():
  if not os.path.isfile(ONCOTREE_FILE):
    print('* Downloading Oncotree file')
    subprocess.run(['curl', ONCOTREE_URL, '--create-dirs', '-o', ONCOTREE_FILE])
  

if __name__ == "__main__":
  data_df = pd.read_csv(META_DATA_FILE, sep='\t')
  sigs_df = pd.read_csv(META_SIGS_FILE, sep='\t')

  create_genes_agg_file()

  file_list = []
  for file_column in META_DATA_FILE_COLS:
    file_list += data_df[file_column].dropna().tolist()
  for file_column in META_SIGS_FILE_COLS:
    file_list += sigs_df[file_column].dropna().tolist()
  download_files(file_list)

  for index, data_row in data_df.iterrows():
    clean_data_files(data_row)
  
  download_oncotree()
  
  print('* Done')