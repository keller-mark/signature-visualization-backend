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

OBJ_DIR = './obj' if bool(os.environ.get("DEBUG", '')) else '/obj'

META_DATA_FILE = os.path.join(OBJ_DIR, META_DATA_FILENAME)

GENES_AGG_FILE = os.path.join(OBJ_DIR, GENES_AGG_FILENAME)

def read_tsv(csv_file_path, **kwargs):
  return pd.read_csv(os.path.join(OBJ_DIR, csv_file_path), sep='\t', **kwargs)

def to_tsv(df, csv_file_path, **kwargs):
  df.to_csv(os.path.join(OBJ_DIR, csv_file_path), sep='\t', **kwargs)

def clean_data_files(data_row):
  
  if pd.notnull(data_row[META_COL_PATH_GENE_MUT]):
    print('* Appending to genes aggregate files')
    genes_df = read_tsv(data_row[META_COL_PATH_GENE_MUT])
    genes_df[META_COL_PROJ] = data_row[META_COL_PROJ]
    genes_df = genes_df.groupby([META_COL_PROJ, GENE_SYMBOL]).size().reset_index(name='count')

    alphabet = string.ascii_uppercase
    for letter in alphabet:
      genes_agg_df = pd.read_csv(GENES_AGG_FILE.format(letter=letter), sep='\t')
      genes_df_by_letter = genes_df.loc[genes_df[GENE_SYMBOL].str.startswith(letter)]
      if genes_df_by_letter.shape[0] > 0:
        genes_agg_df = genes_agg_df.append(genes_df_by_letter, ignore_index=True)
        genes_agg_df.to_csv(GENES_AGG_FILE.format(letter=letter), sep='\t', index=False)

if __name__ == "__main__":
  data_df = pd.read_csv(META_DATA_FILE, sep='\t')
  
  for index, data_row in data_df.iterrows():
    clean_data_files(data_row)
  
  print('* Done')