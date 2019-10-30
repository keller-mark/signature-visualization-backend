import pandas as pd
import json
from web_constants import *
from helpers import pd_fetch_tsv, path_or_none
from oncotree import *

""" Load the metadata file to be able to create SigData objects """
sig_dfs = {}
sig_groups_meta_df = pd.read_csv(META_SIGS_FILE, sep='\t', index_col=0)
sigs_meta_df = pd.DataFrame(data=[], index=[], columns=META_SIGS_COLS + [META_COL_SIG_GROUP])
sigs_cancer_type_map_df = pd.DataFrame(data=[], index=[], columns=META_CANCER_TYPE_MAP_COLS + [META_COL_SIG_GROUP])

""" Load the Oncotree """
with open(ONCOTREE_FILE) as f:
    tree_json = json.load(f)
tree = OncoTree(tree_json)

def prepend_sig_group_to_sig_name(sig_group, sig_name):
    return ("%s %s" % (sig_group, sig_name))

""" Load signatures data """
for sig_group_index, sig_group_row in sig_groups_meta_df.iterrows():
    # Load metadata
    sig_group_meta_df = pd_fetch_tsv(OBJ_DIR, sig_group_row[META_COL_PATH_SIGS_META])
    sig_group_meta_df[META_COL_SIG_GROUP] = sig_group_index
    sigs_meta_df = sigs_meta_df.append(sig_group_meta_df, ignore_index=True)
    # Load cancer type mappings
    sig_group_cancer_type_map_df = pd_fetch_tsv(OBJ_DIR, sig_group_row[META_COL_PATH_SIGS_CANCER_TYPE_MAP])
    sig_group_cancer_type_map_df[META_COL_SIG_GROUP] = sig_group_index
    sigs_cancer_type_map_df = sigs_cancer_type_map_df.append(sig_group_cancer_type_map_df, ignore_index=True)
    # Load signatures data
    for cat_type in CAT_TYPES:
        if pd.notnull(sig_group_row[META_COL_PATH_SIGS_DATA.format(cat_type=cat_type)]):
            sig_df = pd_fetch_tsv(OBJ_DIR, sig_group_row[META_COL_PATH_SIGS_DATA.format(cat_type=cat_type)], index_col=0)
            sig_df.index = sig_df.index.rename(META_COL_SIG)
            sig_df = sig_df.reset_index()
            sig_df[META_COL_SIG] = sig_df[META_COL_SIG].astype(str)
            # Prepend the signature group to the signature names
            sig_df[META_COL_SIG] = sig_df.apply(lambda row: prepend_sig_group_to_sig_name(sig_group_index, row[META_COL_SIG]), axis='columns')

            sig_df = sig_df.set_index(META_COL_SIG, drop=True)
            # Append to the dataframe for the category type
            try:
                sig_dfs[cat_type] = sig_dfs[cat_type].append(sig_df)
            except KeyError:
                sig_dfs[cat_type] = sig_df

sigs_cancer_type_map_df[META_COL_SIG] = sigs_cancer_type_map_df[META_COL_SIG].astype(str)
sigs_meta_df[META_COL_SIG] = sigs_meta_df[META_COL_SIG].astype(str)

# Prepend the signature group to the signature names
sigs_cancer_type_map_df[META_COL_SIG] = sigs_cancer_type_map_df.apply(lambda row: prepend_sig_group_to_sig_name(row[META_COL_SIG_GROUP], row[META_COL_SIG]), axis='columns')
sigs_meta_df[META_COL_SIG] = sigs_meta_df.apply(lambda row: prepend_sig_group_to_sig_name(row[META_COL_SIG_GROUP], row[META_COL_SIG]), axis='columns')

sigs_meta_df = sigs_meta_df.set_index(META_COL_SIG, drop=True)
sigs_meta_df = sigs_meta_df.sort_values(by=META_COL_INDEX)

# Function for getting single SigData object
def get_sig_data(sig_id):
    return SigData(sig_id, sigs_meta_df.loc[sig_id])

def get_selected_sig_data(sig_id_list):
    return list(map(lambda sig_id: get_sig_data(sig_id), sig_id_list))

# Function for getting list of all SigData objects
def get_all_sig_data():
    row_tuples = sigs_meta_df.to_dict(orient='index').items()
    return list(map(lambda row: SigData(row[0], row[1]), row_tuples))

# Function for getting category listing
def get_category_list(cat_type):
    if cat_type in sig_dfs.keys():
        return sig_dfs[cat_type].columns.values.tolist()
    return []

# Function for getting 'serialized' list of all SigData objects
def get_all_sig_data_as_json():
    def sig_data_to_json(obj):
        # Actually just a list of python objects
        return {
            "id": obj.get_sig_id(),
            "group": obj.get_sig_group(),
            "publication": obj.get_publication(),
            "description": obj.get_description(),
            "index": obj.get_index(),
            "cat_type": obj.get_cat_type(),
            "mut_type": obj.get_mut_type()
        }
    return list(map(sig_data_to_json, get_all_sig_data()))

def get_all_cancer_type_mappings_as_json():
    result = []
    for group_ctype_tuple, group_ctype_df in sigs_cancer_type_map_df.groupby([META_COL_SIG_GROUP, META_COL_CANCER_TYPE]):
        group_ctype_df = group_ctype_df.reset_index(drop=True)
        oncotree_code = group_ctype_df.loc[0][META_COL_ONCOTREE_CODE]
        for sig in list(group_ctype_df[META_COL_SIG].unique()):
            result.append({
                'group': group_ctype_tuple[0],
                'cancer_type': group_ctype_tuple[1],
                'oncotree_code': (oncotree_code if pd.notnull(oncotree_code) else "nan"),
                'oncotree_name': ((tree.find_node(oncotree_code).name) if pd.notnull(oncotree_code) else "nan"),
                'signature': sig
            })
    return result

""" 
Class representing a single row of the META_SIGS_FILE
"""
class SigGroupData():

    def __init__(self, sig_group_id, sig_group_row):
        self.sig_group_id = sig_group_id
        self.publication = sig_group_row[META_COL_PUBLICATION]
        
        self.sigs_meta_df = sigs_meta_df.loc[sigs_meta_df[META_COL_SIG_GROUP] == sig_group_id]
        self.cancer_type_map_df = sigs_cancer_type_map_df.loc[sigs_cancer_type_map_df[META_COL_SIG_GROUP] == sig_group_id]
    
    def get_sig_group_id(self):
        return self.sig_group_id
    
    def get_publication(self):
        return self.publication
    
    def get_sigs_meta_df(self):
        return self.sigs_meta_df
    
    def get_cancer_type_map_df(self):
        return self.cancer_type_map_df

"""
Class representing a single signature's metadata
"""
class SigData():
    
    def __init__(self, sig_id, sig_row):
        self.sig_id = str(sig_id)
        self.sig_group = sig_row[META_COL_SIG_GROUP]
        self.publication = sig_groups_meta_df.loc[sig_row[META_COL_SIG_GROUP]][META_COL_PUBLICATION]
        self.description = sig_row[META_COL_DESCRIPTION]
        self.index = sig_row[META_COL_INDEX]
        self.cat_type = sig_row[META_COL_CAT_TYPE]

        self.cancer_type_map_df = sigs_cancer_type_map_df.loc[sigs_cancer_type_map_df[META_COL_SIG] == sig_id]
        self.sig_dict = sig_dfs[self.cat_type].transpose()[sig_id].to_dict()
        self.sig_dict[META_COL_SIG] = self.sig_id
    
    def get_sig_id(self):
        return self.sig_id

    def get_sig_name(self):
        return self.get_sig_id()
    
    def get_sig_group(self):
        return self.sig_group

    def get_publication(self):
        return self.publication if pd.notnull(self.publication) else ""
    
    def get_description(self):
        return self.description if pd.notnull(self.description) else ""
    
    def get_index(self):
        return self.index

    def get_cat_type(self):
        return self.cat_type
    
    def get_mut_type(self):
        return CAT_TYPE_MAP[self.cat_type]
    
    def get_cancer_type_map_df(self):
        return self.cancer_type_map_df
    
    def get_sig_dict(self):
        return self.sig_dict