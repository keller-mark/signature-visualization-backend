import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type


def plot_signature(signature, mut_type, signature_index=None, tricounts_method=None):

    signatures = get_signatures_by_mut_type({mut_type: [signature]}, tricounts_method=tricounts_method)[mut_type]
    sigs_df = signatures.get_df()

    prob_colname = "probability"
    if signature_index != None:
        prob_colname = "sig_{}_{}".format(mut_type, signature_index)


    sigs_list = list(sigs_df.loc[signature, :].to_dict().items())
    result = list(map(lambda cat_array: {"cat_" + mut_type: cat_array[0], prob_colname: cat_array[1]}, sigs_list))
    return result
