import pandas as pd
import subprocess
import os
import sys

# Load our modules
this_file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.normpath(this_file_path + '/../'))
from web_constants import GENE_SYMBOL


OBJ_STORE_URL = "https://mutation-signature-explorer.obj.umiacs.umd.edu/"
FILE_COLUMNS = [
  'path_extended_SBS', 'path_counts_SBS', 
  'path_extended_DBS', 'path_counts_DBS', 
  'path_extended_INDEL', 'path_counts_INDEL', 
  'path_clinical',
  'path_samples',
  'path_genes'
]
OBJ_DIR = '../../obj' if bool(os.environ.get("DEBUG", '')) else '/obj'
META_FILE = './meta.tsv' if bool(os.environ.get("DEBUG", '')) else '/app/data/meta.tsv'
GENES_AGG_FILE = os.path.join(OBJ_DIR, 'genes_agg.tsv')

CLEAN_DATA_PY = 'clean_data.py' if bool(os.environ.get("DEBUG", '')) else '/app/data/clean_data.py'

def create_genes_agg_file():
  genes_agg_df = pd.DataFrame(index=[], columns=["proj_id", GENE_SYMBOL, "count"])
  genes_agg_df.to_csv(GENES_AGG_FILE, sep='\t', index=False)

def download(file_list):
  for file_path in file_list:
    local_file_path = os.path.join(OBJ_DIR, file_path)
    remote_file_url = OBJ_STORE_URL + file_path
    if not os.path.isfile(local_file_path):
      subprocess.run(['curl', remote_file_url, '--create-dirs', '-o', local_file_path])

def clean_samples(proj_id, samples_path, clinical_path, counts_path_sbs, counts_path_dbs, counts_path_indel, genes_path):
  subprocess.run([
    'python', CLEAN_DATA_PY, 
    '-s', os.path.join(OBJ_DIR, samples_path), 
    '-c', os.path.join(OBJ_DIR, clinical_path),
    '-g', (os.path.join(OBJ_DIR, genes_path) if not pd.isna(genes_path) else "None"),
    '-c-sbs', os.path.join(OBJ_DIR, counts_path_sbs),
    '-c-dbs', os.path.join(OBJ_DIR, counts_path_dbs),
    '-c-indel', os.path.join(OBJ_DIR, counts_path_indel),
    '-g-agg', GENES_AGG_FILE,
    '-pid', proj_id
  ])

if __name__ == "__main__":
  create_genes_agg_file()
  file_list = []
  df = pd.read_csv(META_FILE, sep='\t')
  for file_column in FILE_COLUMNS:
    file_list += df[file_column].dropna().tolist()
  download(file_list)
  for index, row in df.iterrows():
    clean_samples(
      row['id'],
      row['path_samples'], 
      row['path_clinical'], 
      row['path_counts_SBS'], 
      row['path_counts_DBS'], 
      row['path_counts_INDEL'],
      row['path_genes']
    )
