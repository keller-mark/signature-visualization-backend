import pandas as pd
import io
import os

def pd_as_file(df, index_val=True):
    output = io.StringIO()
    df.to_csv(output, index=index_val)
    return output.getvalue()

def pd_fetch_tsv(obj_dir, s3_key, **kwargs):
    filepath = os.path.join(obj_dir, s3_key)
    return pd.read_csv(filepath, sep='\t', **kwargs)

def path_or_none(row, index):
    if pd.notnull(row[index]):
        return row[index]
    return None