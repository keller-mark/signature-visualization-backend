import pandas as pd
import numpy as np

from web_constants import *
from sig_data import get_category_list

def scale_contexts(mut_type):
    return get_category_list(MUT_TYPE_MAP[mut_type])

"""
SELECT name 
FROM mut_cat 
WHERE mut_cat.cat_type_id = (SELECT id FROM mut_cat_type WHERE mut_cat_type.name = 'SBS_96')
ORDER BY mut_cat.id ASC
"""