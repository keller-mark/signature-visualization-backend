import pandas as pd
import numpy as np
import os
import io
import re
import sys
import json
from web_constants import *
from signatures import Signatures

class PlotProcessing():

  @staticmethod
  def project_metadata(filepaths = True):
    meta_df = pd.read_csv(DATA_META_FILE, sep='\t', index_col=0)
    meta_df["has_clinical"] = pd.notnull(meta_df["clinical_path"])
    meta_df["has_ssm"] = pd.notnull(meta_df["ssm_path"])
    meta_df["has_counts"] = pd.notnull(meta_df["counts_path"])
    meta_df = meta_df.fillna(value="")
    if not filepaths:
      meta_df = meta_df.drop(columns=['clinical_path', 'ssm_path', 'counts_path'])
    meta_df = meta_df.transpose()
    return meta_df.to_dict()
  
  @staticmethod
  def pd_fetch_tsv(s3_key, **kwargs):
    filepath = os.path.join(OBJ_DIR, s3_key)
    return pd.read_csv(filepath, sep='\t', **kwargs)

  @staticmethod
  def pd_as_file(df, index_val=True):
    output = io.StringIO()
    df.to_csv(output, index=index_val)
    return output.getvalue()

  @staticmethod
  def muts_by_sig_points(region_width, chromosome, sigs, projects):
    signatures = Signatures(SIGS_FILE, SIGS_META_FILE, chosen_sigs=sigs)
    # validation
    if region_width < 10000: # will be too slow, stop processing
      return None
    
    sig_names = signatures.get_chosen_names()
    region_names = list(range(0, CHROMOSOMES[chromosome], region_width))
    # regions_master_df: sigs x regions
    regions_master_df = pd.DataFrame(index=sig_names, columns=region_names)

    project_metadata = PlotProcessing.project_metadata()
    for proj_id in projects:
      if project_metadata[proj_id]["has_ssm"] and project_metadata[proj_id]["has_counts"]:
        ssm_filepath = project_metadata[proj_id]["ssm_path"]
        counts_filepath = project_metadata[proj_id]["counts_path"]

        ssm_df = PlotProcessing.pd_fetch_tsv(ssm_filepath)
        counts_df = PlotProcessing.pd_fetch_tsv(counts_filepath, index_col=0)
        # restrict to current chromosome
        ssm_df = ssm_df[ssm_df[CHR] == chromosome]
        # set region values
        ssm_df['region'] = ssm_df.apply(lambda row: row[POS] // region_width * region_width, axis=1) 

        # set signature values
        # compute exposures
        counts_df = counts_df.dropna(axis=0, how='any')

        if len(counts_df) > 0:
          exps_df = signatures.get_exposures(counts_df)
          # compute assignments
          assignments_df = signatures.get_assignments(exps_df)
          # add signature column
          ssm_df['signature'] = ssm_df.apply(lambda row: assignments_df.loc[row[SAMPLE], row[CAT]] if pd.notnull(row[CAT]) else None, axis=1)
          
          # aggregate
          groups = ssm_df.groupby(['region', 'signature'])
          counts = groups.size().reset_index(name='counts')   
          regions_df = counts.pivot(index='signature', columns='region', values='counts')
          # sum
          regions_master_df = regions_master_df.add(regions_df, fill_value=0)
    
    # finalize
    regions_master_df.fillna(value=0, inplace=True)
    regions_master_df[list(regions_master_df.columns.values)] = regions_master_df[list(regions_master_df.columns.values)].astype(int)
    return PlotProcessing.pd_as_file(regions_master_df.transpose())

  @staticmethod
  def sigs():
    sig_df = pd.read_csv(SIGS_FILE, sep='\t', index_col=0)
    return PlotProcessing.pd_as_file(sig_df)

  @staticmethod
  def sigs_per_cancer_type():
    if not os.path.isfile(SIGS_PER_CANCER_TYPE_FILE):
      return None
    with open(SIGS_PER_CANCER_TYPE_FILE) as data_file:    
      active_sigs = json.load(data_file)
    return active_sigs

  @staticmethod
  def data_listing_json():
    signatures = Signatures(SIGS_FILE, SIGS_META_FILE)
    return {
      "sources": PlotProcessing.project_metadata(filepaths = False),
      "sigs": signatures.get_metadata(),
      "sig_presets": PlotProcessing.sigs_per_cancer_type()
    }

  @staticmethod
  def kataegis(projects):
    width = 1000
    df_cols = [SAMPLE, CHR, POS]
    df = pd.DataFrame([], columns=df_cols)
    result = {
      # sets of kataegis mutations by donor, chromosome
      # 'SAMPLE': { '1': list(mutation_1, mutation_2), ... }
    }
    project_metadata = PlotProcessing.project_metadata()
    for proj_id in projects:
      if project_metadata[proj_id]["has_ssm"]:
        ssm_filepath = project_metadata[proj_id]["ssm_path"]
        ssm_df = PlotProcessing.pd_fetch_tsv(ssm_filepath)
        katagis_df = ssm_df.loc[ssm_df[MUT_DIST_ROLLING_MEAN] <= width][df_cols]
        df = df.append(katagis_df, ignore_index=True)
        # create empty entry for each donor
        proj_donor_ids = list(ssm_df[SAMPLE].unique())
        for donor_id in proj_donor_ids:
          result[donor_id] = { 'kataegis': {}, 'proj_id': proj_id }
    
    groups = df.groupby([SAMPLE, CHR])
    def add_group(g):
      g_donor_id = g[SAMPLE].unique()[0]
      g_chromosome = g[CHR].unique()[0]
      g_kataegis_mutations = list(g[POS].unique())
      result[g_donor_id]['kataegis'][g_chromosome] = g_kataegis_mutations

    groups.apply(add_group)

    return result
  
  @staticmethod
  def kataegis_rainfall(proj_id, donor_id, chromosome):
    project_metadata = PlotProcessing.project_metadata()

    df_cols = [SAMPLE, CHR, POS, CAT, CAT_INDEX, MUT_DIST, MUT_DIST_ROLLING_MEAN]
    ssm_df = pd.DataFrame([], columns=df_cols)
    if project_metadata[proj_id]["has_ssm"]:
      ssm_filepath = project_metadata[proj_id]["ssm_path"]
      ssm_df = PlotProcessing.pd_fetch_tsv(ssm_filepath)
      ssm_df = ssm_df.loc[ssm_df[CHR] == chromosome][df_cols]
      ssm_df = ssm_df.loc[ssm_df[SAMPLE] == donor_id][df_cols]

      ssm_df['kataegis'] = ssm_df.apply(lambda row: 1 if (row[MUT_DIST_ROLLING_MEAN] <= 1000) else 0, axis=1)
      ssm_df = ssm_df.drop(columns=[MUT_DIST_ROLLING_MEAN, CHR, SAMPLE])
      ssm_df = ssm_df.replace([np.inf, -np.inf], np.nan)
      ssm_df = ssm_df.dropna(axis=0, how='any', subset=[CAT, MUT_DIST])
      ssm_df[MUT_DIST] = ssm_df[MUT_DIST].astype(int)
      ssm_df[CAT_INDEX] = ssm_df[CAT_INDEX].astype(int)
      ssm_df = ssm_df.rename(columns={ POS: "pos", CAT: "cat", CAT_INDEX: "cat_index", MUT_DIST: "mut_dist" })
    return PlotProcessing.pd_as_file(ssm_df, index_val=False)
  
  @staticmethod
  def signature_exposures(sigs, projects):
    signatures = Signatures(SIGS_FILE, SIGS_META_FILE, chosen_sigs=sigs)
    
    sig_names = signatures.get_chosen_names()
    result_df = pd.DataFrame([], columns=CLINICAL_VARIABLES + sig_names)
    project_metadata = PlotProcessing.project_metadata()
    for proj_id in projects:
      if project_metadata[proj_id]["has_counts"]:
        counts_filepath = project_metadata[proj_id]["counts_path"]
        counts_df = PlotProcessing.pd_fetch_tsv(counts_filepath, index_col=0)
        if project_metadata[proj_id]["has_clinical"]:
          donor_filepath = project_metadata[proj_id]["clinical_path"]
          clinical_df = PlotProcessing.pd_fetch_tsv(donor_filepath, index_col=0)
        else:
          clinical_df = pd.DataFrame([], columns=CLINICAL_VARIABLES, index=list(counts_df.index.values))
        
        mutation_categories = list(counts_df.columns.values)

        if len(counts_df) > 0:
          # compute exposures
          exps_df = signatures.get_exposures(counts_df)

          # multiply exposures by total mutations for each donor
          exps_df = exps_df.apply(lambda row: row * counts_df.loc[row.name, :].sum(), axis=1)

          # join exposures and clinical data
          clinical_df = clinical_df.join(exps_df)
          # drop donors with empty exposures, didn't have count data
          clinical_df = clinical_df.dropna(subset=sigs, how='any')
          # add column for project id
          clinical_df.loc[:, 'proj_id'] = proj_id
          # append project df to overall df
          result_df = result_df.append(clinical_df)
    result_df.index.name = 'donor_id'
    # finalize
    return PlotProcessing.pd_as_file(result_df)
  
  @staticmethod
  def chromosome_bands():
    df = pd.read_csv(CHROMOSOME_BANDS_FILE, sep='\t')

    return PlotProcessing.pd_as_file(df, index_val=False)
