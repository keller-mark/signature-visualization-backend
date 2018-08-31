import pandas as pd
import io

def pd_as_file(df, index_val=True):
    output = io.StringIO()
    df.to_csv(output, index=index_val)
    return output.getvalue()