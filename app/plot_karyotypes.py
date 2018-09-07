import pandas as pd

from web_constants import *
from helpers import pd_as_file

def plot_karyotypes():
  df = pd.read_csv(CHROMOSOME_BANDS_FILE, sep='\t')
  return pd_as_file(df, index_val=False)