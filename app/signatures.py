import logging
import sys
import os
import pandas as pd
import numpy as np

from web_constants import *
from sig_data import *

parent_dir_name = os.path.dirname(os.path.realpath(__file__))
sys.path.append(parent_dir_name + "/signature-estimation-py")
from signature_estimation import signature_estimation, QP

def get_signatures_by_mut_type(chosen_sigs_by_mut_type):
    result = {}
    for mut_type, chosen_sig_ids in chosen_sigs_by_mut_type.items():
        chosen_sigs = [get_sig_data(sig_id) for sig_id in chosen_sig_ids]
        result[mut_type] = Signatures(cat_type=MUT_TYPE_MAP[mut_type], chosen_sigs=chosen_sigs)
    return result

class Signatures():

    def __init__(self, cat_type, chosen_sigs=[]):
        self.cat_type = cat_type
        self.chosen_sigs = chosen_sigs
        self.sigs_df = pd.DataFrame(index=[], data=[], columns=[META_COL_SIG])
        for sig in chosen_sigs:
            self.sigs_df = self.sigs_df.append(sig.get_sig_dict(), ignore_index=True)
        self.sigs_df = self.sigs_df.set_index(META_COL_SIG, drop=True)

    def get_cat_type(self):
        return self.cat_type

    def get_chosen_names(self):
        return [sig.get_sig_name() for sig in self.chosen_sigs]
    
    def get_contexts(self):
        return list(self.sigs_df.columns.values)

    def get_2d_array(self):
        return self.sigs_df.values

    def get_df(self):
        return self.sigs_df
    
    def get_counts(self, ssm_df):
        ssm_df = ssm_df[pd.notnull(ssm_df[CAT])]
        # Initialize donor_id x 96 context df to hold mutation context counts
        tc_df = pd.DataFrame(data=0, columns=self.get_contexts(), index=list(ssm_df[SAMPLE].unique()))
        # aggregate
        groups = ssm_df.groupby([SAMPLE, CAT])
        counts = groups.size().reset_index(name='counts')   
        partial_tc_df = counts.pivot(index=SAMPLE, columns=CAT, values='counts')
        # expand back out
        tc_df = tc_df.add(partial_tc_df, fill_value=0)
        return tc_df

    def get_exposures(self, counts_df):
        sig_names = self.get_chosen_names()
        samples = list(counts_df.index)
        categories = self.get_contexts()

        counts_df = counts_df[categories]

        M = counts_df.values
        P = self.get_2d_array() # (active) signatures matrix
        E = signature_estimation(M, P, QP)

        exps_df = pd.DataFrame(E, index=samples, columns=sig_names)
        return exps_df
        
    def get_assignments(self, exps_df):
        sig_names = self.get_chosen_names()
        # Assignments dataset (samples x mutation contexts)
        assignments_df = pd.DataFrame(index=exps_df.index.values, columns=self.get_contexts())

        # Iterate over samples and mutation contexts
        for sample_id in exps_df.index.values:
            for mut_context in self.get_contexts():
                sample_exposures = exps_df.loc[sample_id, sig_names]
                context_probabilities = self.sigs_df.loc[sig_names, mut_context]
                # Multiply row of 
                # signature exposures and 
                # column of probabilities of the context in each signature
                exposures_by_probabilities = np.multiply(sample_exposures.values, context_probabilities.values)
                # Get index of the max of the 30 values produced above 
                # => index of the signature to assign to this sample for this context
                max_sig_index = np.argmax(exposures_by_probabilities)
                # Add one since signature numbering is 1-indexed (1:30)
                assignments_df.at[sample_id, mut_context] = sig_names[max_sig_index]

        return assignments_df
    
