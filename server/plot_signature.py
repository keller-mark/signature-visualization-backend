import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type


def plot_signature(signature, mut_type, tricounts_method=None):

    signatures = get_signatures_by_mut_type({mut_type: [signature]}, tricounts_method=tricounts_method)[mut_type]
    sigs_df = signatures.get_df()

    sigs_list = list(sigs_df.loc[signature, :].to_dict().items())
    result = list(map(lambda cat_array: {"cat_" + mut_type: cat_array[0],  "sig_prob_" + mut_type: cat_array[1]}, sigs_list))
    return result

"""
SELECT 
	mut_cat.name,
	sig_cat_by_sig.value
FROM (
    SELECT 
        sig_cat.cat_id,
        sig_cat.value
    FROM sig_cat
    WHERE sig_cat.sig_id = (
        SELECT sig.id 
        FROM sig 
        LEFT JOIN sig_group
            ON sig_group.id = sig.group_id
        WHERE CONCAT(sig_group.name, " ", sig.name) = 'COSMIC 1'

    )
) AS sig_cat_by_sig
LEFT JOIN mut_cat
	ON mut_cat.id = sig_cat_by_sig.cat_id
"""