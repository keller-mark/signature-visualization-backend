import pandas as pd
import subprocess
import os
import sys
import json
import string


# Load our modules
this_file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.normpath(this_file_path + '/../'))
from web_constants import *
from oncotree import *

OBJ_DIR = '/obj'

META_DATA_FILE = os.path.join(OBJ_DIR, META_DATA_FILENAME)
META_SIGS_FILE = os.path.join(OBJ_DIR, META_SIGS_FILENAME)
META_PATHWAYS_FILE = os.path.join(OBJ_DIR, META_PATHWAYS_FILENAME)
META_FEATURED_FILE = os.path.join(OBJ_DIR, META_FEATURED_FILENAME)
META_TRICOUNTS_FILE = os.path.join(OBJ_DIR, META_TRICOUNTS_FILENAME)

ONCOTREE_FILE = os.path.join(OBJ_DIR, ONCOTREE_FILENAME)

OBJ_STORE_URL = "https://mutation-signature-explorer.obj.umiacs.umd.edu/"
ONCOTREE_URL = "http://oncotree.mskcc.org/api/tumorTypes/tree?version=oncotree_2018_11_01"


def download_files(file_list):
  for file_path in file_list:
    local_file_path = os.path.join(OBJ_DIR, file_path)
    remote_file_url = OBJ_STORE_URL + file_path
    if not os.path.isfile(local_file_path):
      print('* Downloading ' + local_file_path)
      subprocess.run(['curl', remote_file_url, '--create-dirs', '-o', local_file_path])
    else:
      print('* Not downloading ' + local_file_path)


def download_oncotree():
  if not os.path.isfile(ONCOTREE_FILE):
    print('* Downloading Oncotree file')
    subprocess.run(['curl', ONCOTREE_URL, '--create-dirs', '-o', ONCOTREE_FILE])
  else:
    print('* Not downloading Oncotree file')


if __name__ == "__main__":
    data_df = pd.read_csv(META_DATA_FILE, sep='\t')
    sigs_df = pd.read_csv(META_SIGS_FILE, sep='\t')
    pathways_df = pd.read_csv(META_PATHWAYS_FILE, sep='\t')
    tricounts_df = pd.read_csv(META_TRICOUNTS_FILE, sep='\t')

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
    
    download_oncotree()
    
    print('* Done downloading')