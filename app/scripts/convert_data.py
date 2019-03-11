import pandas as pd
import os
import sys


# Load our modules
this_file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.normpath(this_file_path + '/../'))
from web_constants import *

OBJ_DIR = './obj' if bool(os.environ.get("DEBUG", '')) else '/obj'

META_DATA_FILE = os.path.join(OBJ_DIR, META_DATA_FILENAME)


def read_tsv(tsv_file_path):
    return pd.read_csv(os.path.join(OBJ_DIR, tsv_file_path), sep='\t')

def to_parquet(df, tsv_file_path):
    parquet_file_path = tsv_file_path[:-3] + "parquet"
    df.to_parquet(os.path.join(OBJ_DIR, parquet_file_path), engine='fastparquet', compression='snappy', index=False)

def convert_data_file(tsv_file_path):
    to_parquet(read_tsv(tsv_file_path), tsv_file_path)

if __name__ == "__main__":
    print('* Converting tsv files to parquet files')
    data_df = pd.read_csv(META_DATA_FILE, sep='\t')
  
    file_list = []
    for file_column in META_DATA_FILE_COLS:
        file_list += data_df[file_column].dropna().tolist()

    for file_path in file_list:
        convert_data_file(file_path)
  
    print('* Done')