import sys, os, argparse, numpy as np, pandas as pd

# Load our modules
this_file_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.normpath(this_file_path + '/../'))
from web_constants import *

# Parse arguments
def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--samples-file', type=str, required=True)
    parser.add_argument('-c', '--clinical-file', type=str, required=True)
    parser.add_argument('-c-sbs', '--counts-sbs-file', type=str, required=True)
    parser.add_argument('-c-dbs', '--counts-dbs-file', type=str, required=True)
    parser.add_argument('-c-indel', '--counts-indel-file', type=str, required=True)
    return parser

def run( args ):

    print('* Cleaning sample data...')
    # load data
    samples_df = pd.read_csv(args.samples_file, sep='\t', usecols=[PATIENT, SAMPLE])
    samples_df = samples_df.set_index(SAMPLE, drop=True)

    clinical_df = pd.read_csv(args.clinical_file, sep='\t')
    clinical_df = clinical_df.set_index(PATIENT, drop=True)

    counts_df_sbs = pd.read_csv(args.counts_sbs_file, sep='\t', index_col=0)
    counts_df_dbs = pd.read_csv(args.counts_dbs_file, sep='\t', index_col=0)
    counts_df_indel = pd.read_csv(args.counts_indel_file, sep='\t', index_col=0)

    # join all counts dfs
    counts_df = pd.DataFrame(index=[], data=[])
    counts_df = counts_df.join(counts_df_sbs, how='outer')
    counts_df = counts_df.join(counts_df_dbs, how='outer')
    counts_df = counts_df.join(counts_df_indel, how='outer')

    # filter and save new samples file
    samples_counts_df = counts_df.join(samples_df, how='left')
    samples_counts_df.index = samples_counts_df.index.rename(SAMPLE)
    samples_counts_df = samples_counts_df.reset_index()
    samples_filtered_df = samples_counts_df[[PATIENT, SAMPLE]]
    samples_filtered_df.to_csv(args.samples_file, sep='\t', index=False)

    # filter and save new clinical file
    samples_filtered_df = samples_filtered_df.drop_duplicates(subset=[PATIENT])
    samples_filtered_df = samples_filtered_df.set_index(PATIENT, drop=True)
    clinical_samples_df = samples_filtered_df.join(clinical_df, how='left')
    clinical_filtered_df = clinical_samples_df.drop(columns=[SAMPLE])
    clinical_filtered_df = clinical_filtered_df.reset_index()
    clinical_filtered_df.to_csv(args.clinical_file, sep='\t', index=False)


if __name__ == '__main__': run( get_parser().parse_args(sys.argv[1:]) )
