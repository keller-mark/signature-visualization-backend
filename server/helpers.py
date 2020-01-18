import pandas as pd
import io
import os

def pd_as_file(df, index_val=True):
    output = io.StringIO()
    df.to_csv(output, index=index_val)
    return output.getvalue()

def pd_fetch_tsv(obj_dir, s3_key, **kwargs):
    filepath = os.path.join(obj_dir, s3_key)
    parquet_filepath = filepath[:-3] + "parquet"
    if os.path.isfile(parquet_filepath):
        try:
            usecols = list(kwargs.pop('usecols'))
        except KeyError:
            usecols = None
        return pd.read_parquet(parquet_filepath, columns=usecols, engine='fastparquet', **kwargs)
    return pd.read_csv(filepath, sep='\t', **kwargs)

def path_or_none(row, index):
    if pd.notnull(row[index]):
        return row[index]
    return None