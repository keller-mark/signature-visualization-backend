import pandas as pd
import numpy as np
import scipy.cluster
import os
import io
import re
import sys
import json
from functools import reduce
from yaml import load
from yaml import Loader
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
      meta_df = meta_df.drop(columns=['clinical_path', 'ssm_path', 'counts_path', 'genome_events_path'])
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
  def signature_genome_bins(region_width, sigs, projects, single_donor_id=None):
    signatures = Signatures(SIGS_FILE, SIGS_META_FILE, chosen_sigs=sigs)
    # validation
    if region_width < 10000: # will be too slow, stop processing
      return None

    if single_donor_id != None: # single donor request
      assert(len(projects) == 1)
    
    sig_names = signatures.get_chosen_names()
    chr_dfs = {}
    for chr_name, chr_len in CHROMOSOMES.items():
      chr_regions = list(range(0, chr_len, region_width))
      # each chr_df: sigs x regions
      chr_dfs[chr_name] = pd.DataFrame(index=sig_names, columns=chr_regions)

    project_metadata = PlotProcessing.project_metadata()
    for proj_id in projects:
      # load data for project
      if project_metadata[proj_id]["has_ssm"] and project_metadata[proj_id]["has_counts"]:
        ssm_filepath = project_metadata[proj_id]["ssm_path"]
        counts_filepath = project_metadata[proj_id]["counts_path"]

        ssm_df = PlotProcessing.pd_fetch_tsv(ssm_filepath)
        counts_df = PlotProcessing.pd_fetch_tsv(counts_filepath, index_col=0)
        counts_df = counts_df.dropna(axis=0, how='any')
        
        if single_donor_id != None: # single donor request
          counts_df = counts_df.loc[[single_donor_id], :]
          ssm_df = ssm_df.loc[ssm_df[SAMPLE] == single_donor_id]

        if len(counts_df) > 0:
          # compute exposures
          exps_df = signatures.get_exposures(counts_df)
          assignments_df = signatures.get_assignments(exps_df)
          # set region of genome
          ssm_df['region'] = ssm_df.apply(lambda row: row[POS] // region_width * region_width, axis=1)
          # add signature column. TODO: figure out why this step takes so long
          ssm_df['signature'] = ssm_df.apply(lambda row: assignments_df.loc[row[SAMPLE], row[CAT]] if pd.notnull(row[CAT]) else None, axis=1)
          # for each chromosome
          for chr_name, ssm_chr_df in ssm_df.groupby([CHR]):
            # aggregate
            groups = ssm_chr_df.groupby(['region', 'signature'])
            counts = groups.size().reset_index(name='counts')   
            regions_df = counts.pivot(index='signature', columns='region', values='counts')
            # sum
            chr_dfs[chr_name] = chr_dfs[chr_name].add(regions_df, fill_value=0)
    
    # finalize
    for chr_name in CHROMOSOMES.keys():
      chr_dfs[chr_name].fillna(value=0, inplace=True)
      chr_dfs[chr_name][list(chr_dfs[chr_name].columns.values)] = chr_dfs[chr_name][list(chr_dfs[chr_name].columns.values)].astype(int)
      chr_dfs[chr_name] = chr_dfs[chr_name].transpose().to_dict(orient='index')
    return chr_dfs

  @staticmethod
  def signature(name):
    signatures = Signatures(SIGS_FILE, SIGS_META_FILE)
    return signatures.get_sig_as_dict(name)

  @staticmethod
  def sigs_per_cancer_type():
    if not os.path.isfile(SIGS_PER_CANCER_TYPE_FILE):
      return None
    with open(SIGS_PER_CANCER_TYPE_FILE) as data_file:    
      active_sigs = load(data_file, Loader=Loader)
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
  def kataegis_rainfall(proj_id, donor_id):
    project_metadata = PlotProcessing.project_metadata()

    df_cols = [SAMPLE, CHR, POS, CAT, CAT_INDEX, MUT_DIST, MUT_DIST_ROLLING_MEAN]
    ssm_df = pd.DataFrame([], columns=df_cols)
    if project_metadata[proj_id]["has_ssm"]:
      ssm_filepath = project_metadata[proj_id]["ssm_path"]
      ssm_df = PlotProcessing.pd_fetch_tsv(ssm_filepath)
      ssm_df = ssm_df.loc[ssm_df[SAMPLE] == donor_id][df_cols]

      ssm_df['kataegis'] = ssm_df.apply(lambda row: 1 if (row[MUT_DIST_ROLLING_MEAN] <= 1000) else 0, axis=1)
      ssm_df = ssm_df.drop(columns=[MUT_DIST_ROLLING_MEAN, SAMPLE])
      ssm_df = ssm_df.replace([np.inf, -np.inf], np.nan)
      ssm_df = ssm_df.dropna(axis=0, how='any', subset=[CAT, MUT_DIST])
      ssm_df[MUT_DIST] = ssm_df[MUT_DIST].astype(int)
      ssm_df[CAT_INDEX] = ssm_df[CAT_INDEX].astype(int)
      ssm_df = ssm_df.rename(columns={ CHR: "chr", POS: "pos", CAT: "cat", CAT_INDEX: "cat_index", MUT_DIST: "mut_dist" })
    return PlotProcessing.pd_as_file(ssm_df, index_val=False)
  
  @staticmethod
  def signature_exposures(sigs, projects, single_donor_id=None):
    signatures = Signatures(SIGS_FILE, SIGS_META_FILE, chosen_sigs=sigs)
    sig_names = signatures.get_chosen_names()
    result = []

    if single_donor_id != None: # single donor request
      assert(len(projects) == 1)
    
    project_metadata = PlotProcessing.project_metadata()
    for proj_id in projects:
      if project_metadata[proj_id]["has_counts"]:
        # counts data
        counts_filepath = project_metadata[proj_id]["counts_path"]
        counts_df = PlotProcessing.pd_fetch_tsv(counts_filepath, index_col=0)
        if single_donor_id != None: # single donor request
          counts_df = counts_df.loc[[single_donor_id], :]
        counts_df = counts_df.dropna(how='any', axis='index')
        donors = list(counts_df.index.values)
        # clinical data
        clinical_df = pd.DataFrame([], columns=[], index=donors)
        if project_metadata[proj_id]["has_clinical"]:
          donor_filepath = project_metadata[proj_id]["clinical_path"]
          temp_clinical_df = PlotProcessing.pd_fetch_tsv(donor_filepath, index_col=0)
          clinical_df = clinical_df.join(temp_clinical_df, how='left')
        clinical_df = clinical_df.fillna(value='nan')
        
        if len(counts_df) > 0:
          # compute exposures
          exps_df = signatures.get_exposures(counts_df)
          # multiply exposures by total mutations for each donor
          exps_df = exps_df.apply(lambda row: row * counts_df.loc[row.name, :].sum(), axis=1)

          # convert dfs to single array
          exps_dict = exps_df.to_dict(orient='index')
          clinical_dict = clinical_df.to_dict(orient='index')
          def create_donor_obj(donor_id):
            return {
              "donor_id": donor_id,
              "proj_id": proj_id,
              "exposures": exps_dict[donor_id],
              "clinical": clinical_dict[donor_id]
            }
          proj_result = list(map(create_donor_obj, donors))
          # concatenate project array into result array
          result = (result + proj_result)
    return result
  

  @staticmethod
  def samples_with_signatures(sigs, projects):
    signatures = Signatures(SIGS_FILE, SIGS_META_FILE, chosen_sigs=sigs)
    sig_names = signatures.get_chosen_names()
    
    # array containing an object for each signature
    # example: { signatures: {"SBS 1": {"proj_id": number, ...}, ...}, "projects": { "proj_id": num_samples}, ... }
    result = {
      "signatures": {},
      "projects": {}
    }

    project_metadata = PlotProcessing.project_metadata()
    for proj_id in projects:
      if project_metadata[proj_id]["has_counts"]:
        # counts data
        counts_filepath = project_metadata[proj_id]["counts_path"]
        counts_df = PlotProcessing.pd_fetch_tsv(counts_filepath, index_col=0)
        counts_df = counts_df.dropna(how='any', axis='index')
        result["projects"][proj_id] = len(counts_df.index.values)
        
        if len(counts_df) > 0:
          # compute exposures
          exps_df = signatures.get_exposures(counts_df)
          # multiply exposures by total mutations for each donor
          exps_df = exps_df.apply(lambda row: row * counts_df.loc[row.name, :].sum(), axis=1)
          # for each signature, get number of samples with at least one mutation attributed
          samples_with_sig = exps_df.apply(lambda col: col.loc[col >= 1].size, axis='index')
          
          for sig_name, num_samples in samples_with_sig.to_dict().items():
            try:
              result["signatures"][sig_name][proj_id] = num_samples
            except KeyError:
              result["signatures"][sig_name] = { proj_id: num_samples }
    return result
  
  @staticmethod
  def chromosome_bands():
    df = pd.read_csv(CHROMOSOME_BANDS_FILE, sep='\t')

    return PlotProcessing.pd_as_file(df, index_val=False)
  
  @staticmethod
  def clustering(sigs, projects):
    signatures = Signatures(SIGS_FILE, SIGS_META_FILE, chosen_sigs=sigs)
    sig_names = signatures.get_chosen_names()
    full_exps_df = pd.DataFrame(index=[], columns=sig_names)
    
    project_metadata = PlotProcessing.project_metadata()
    for proj_id in projects:
      if project_metadata[proj_id]["has_counts"]:
        # counts data
        counts_filepath = project_metadata[proj_id]["counts_path"]
        counts_df = PlotProcessing.pd_fetch_tsv(counts_filepath, index_col=0)
        counts_df = counts_df.dropna(how='any', axis='index')
        
        if len(counts_df) > 0:
          # compute exposures
          exps_df = signatures.get_exposures(counts_df)

          full_exps_df = full_exps_df.append(exps_df, ignore_index=False)

    # Do hierarchical clustering 
    # Reference: https://gist.github.com/mdml/7537455
    observation_vectors = full_exps_df.values
    Z = scipy.cluster.hierarchy.linkage(observation_vectors, method='ward')
    T = scipy.cluster.hierarchy.to_tree(Z)

    # Create dictionary for labeling nodes by their IDs
    labels = list(full_exps_df.index.values)
    id2label = dict(zip(range(len(labels)), labels))

    # Create a nested dictionary from the ClusterNode's returned by SciPy
    def add_node(node, parent):
      # First create the new node and append it to its parent's children
      new_node = dict( node_id=node.id, children=[] )
      parent["children"].append( new_node )
      # Recursively add the current node's children
      if node.left: add_node( node.left, new_node )
      if node.right: add_node( node.right, new_node )
    
    # Initialize nested dictionary for d3, then recursively iterate through tree
    tree_dict = dict(children=[], name="root")
    add_node( T, tree_dict )
  
    # Label each node with the names of each leaf in its subtree
    def label_tree( n ):
      # If the node is a leaf, then we have its name
      if len(n["children"]) == 0:
        leaf_names = [ id2label[n["node_id"]] ]
      # If not, flatten all the leaves in the node's subtree
      else:
        leaf_names = reduce(lambda ls, c: ls + label_tree(c), n["children"], [])
      # Delete the node id since we don't need it anymore and it makes for cleaner JSON
      del n["node_id"]
      # Labeling convention: "-"-separated leaf names
      n["name"] = name = "-".join(sorted(map(str, leaf_names)))
      return leaf_names

    label_tree( tree_dict["children"][0] )
    return tree_dict

  @staticmethod
  def genome_event_track(gene_id, projects):
    result = {}
    
    project_metadata = PlotProcessing.project_metadata()
    for proj_id in projects:
      # TODO: using counts file right now only to get donor list. in future, use sample file
      counts_filepath = project_metadata[proj_id]["counts_path"]
      counts_df = PlotProcessing.pd_fetch_tsv(counts_filepath, index_col=0)
      counts_df = counts_df.dropna(how='any', axis='index')
      donors = list(counts_df.index.values)

      # TODO: get filename from project_metadata
      events_filepath = "genome_events/ICGC/test_data.ICGC-BRCA-EU.tsv"
      events_df = PlotProcessing.pd_fetch_tsv(events_filepath)

      gene_events_df = events_df.loc[events_df['gene_id'] == gene_id]
      gene_events_df = gene_events_df.set_index('sample_id')

      # TODO: change from donors to samples
      for sample_id in donors:
        try:
          event = gene_events_df.loc[sample_id]['event_type']
        except KeyError:
          event = 0
        result[sample_id] = {
          "donor_id": sample_id,
          "proj_id": proj_id,
          "event": str(event)
        }
    return result
