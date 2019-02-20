import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type


def plot_signature(signature, mut_type, tricounts_method=None):

    signatures = get_signatures_by_mut_type({mut_type: [signature]}, tricounts_method=tricounts_method)[mut_type]
    sigs_df = signatures.get_df()

    sigs_list = list(sigs_df.loc[signature, :].to_dict().items())
    result = list(map(lambda cat_array: {"cat_" + mut_type: cat_array[0], "probability": cat_array[1]}, sigs_list))
    return result
