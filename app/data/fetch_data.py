import pandas as pd
import subprocess
import os

OBJ_STORE_URL = "https://mutation-signature-explorer.obj.umiacs.umd.edu/"
FILE_COLUMNS = [
  'path_extended_SBS', 'path_counts_SBS', 
  'path_extended_DBS', 'path_counts_DBS', 
  'path_extended_INDEL', 'path_counts_INDEL', 
  'path_clinical',
  'path_samples'
]
OBJ_DIR = '../../obj' if bool(os.environ.get("DEBUG", '')) else '/obj'
META_FILE = './meta.tsv' if bool(os.environ.get("DEBUG", '')) else '/app/data/meta.tsv'

def download(file_list):
  for file_path in file_list:
    local_file_path = os.path.join(OBJ_DIR, file_path)
    remote_file_url = OBJ_STORE_URL + file_path
    if not os.path.isfile(local_file_path):
      subprocess.run(['curl', remote_file_url, '--create-dirs', '-o', local_file_path])

def clean_samples(samples_path, clinical_path, counts_path_sbs, counts_path_dbs, counts_path_indel):
  subprocess.run([
    'python', 'clean_data.py', 
    '-s', os.path.join(OBJ_DIR, samples_path), 
    '-c', os.path.join(OBJ_DIR, clinical_path),
    '-c-sbs', os.path.join(OBJ_DIR, counts_path_sbs),
    '-c-dbs', os.path.join(OBJ_DIR, counts_path_dbs),
    '-c-indel', os.path.join(OBJ_DIR, counts_path_indel)
  ])

if __name__ == "__main__":
  file_list = []
  df = pd.read_csv(META_FILE, sep='\t')
  for file_column in FILE_COLUMNS:
    file_list += df[file_column].dropna().tolist()
  download(file_list)
  for index, row in df.iterrows():
    clean_samples(row['path_samples'], row['path_clinical'], row['path_counts_SBS'], row['path_counts_DBS'], row['path_counts_INDEL'])
