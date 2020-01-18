import pandas as pd
import numpy as np

from web_constants import *
from sig_data import get_category_list

def scale_contexts(mut_type):
    return get_category_list(MUT_TYPE_MAP[mut_type])