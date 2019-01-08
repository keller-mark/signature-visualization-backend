import pandas as pd
import json
from web_constants import *
from helpers import pd_fetch_tsv, path_or_none
from oncotree import *

""" Load the metadata file to be able to create ProjectData objects """
meta_df = pd.read_csv(META_DATA_FILE, sep='\t', index_col=0)
sigs_mapping_df = pd.read_csv(PROJ_TO_SIGS_FILE, sep='\t')

samples_agg_df = pd.read_csv(SAMPLES_AGG_FILE, sep='\t', index_col=0)

""" Load the Oncotree """
with open(ONCOTREE_FILE) as f:
    tree_json = json.load(f)
tree = OncoTree(tree_json)

# Factory-type function for getting single ProjectData object
def get_project_data(proj_id):
    return ProjectData(proj_id, meta_df.loc[proj_id])

def get_selected_project_data(proj_id_list):
    return list(map(lambda proj_id: get_project_data(proj_id), proj_id_list))

# Factory-type function for getting list of all ProjectData objects
def get_all_project_data():
    row_tuples = meta_df.to_dict(orient='index').items()
    return list(map(lambda row: ProjectData(row[0], row[1]), row_tuples))

# Factory-type function for getting 'serialized' list of all ProjectData objects
def get_all_project_data_as_json():
    def project_data_to_json(obj):
        # Even though this says as_json it is really a list of python objects
        oncotree_code = obj.get_oncotree_code()
        oncotree_name = obj.get_oncotree_name()
        oncotree_tissue_code = obj.get_oncotree_tissue_code()
        return {
            "id": obj.get_proj_id(),
            "name": obj.get_proj_name(),
            "num_samples": obj.get_proj_num_samples(),
            "source": obj.get_proj_source(),
            "has_clinical": obj.has_clinical_df(),
            "has_genes": obj.has_genes_df(),
            "sigs_mapping": obj.get_sigs_mapping(),
            "oncotree_code": (oncotree_code if oncotree_code is not None else "nan"),
            "oncotree_name": (oncotree_name if oncotree_name is not None else "nan"),
            "oncotree_tissue_code": (oncotree_tissue_code if oncotree_tissue_code is not None else "nan")
        }
    return list(map(project_data_to_json, get_all_project_data()))

def get_all_tissue_types_as_json():
    return [{'oncotree_name':node.name, 'oncotree_code':node.code} for node in tree.get_tissue_nodes()]

""" 
Class representing a single row of the META_DATA_FILE, 
also how the files referenced within the meta file should be loaded into data frames
"""
class ProjectData():
    
    def __init__(self, proj_id, proj_row):
        self.proj_id = proj_id
        self.proj_name = proj_row[META_COL_PROJ_NAME]
        self.oncotree_code = proj_row[META_COL_ONCOTREE_CODE] if pd.notnull(proj_row[META_COL_ONCOTREE_CODE]) else None
        self.oncotree_node = tree.find_node(self.oncotree_code) if pd.notnull(proj_row[META_COL_ONCOTREE_CODE]) else None
        self.proj_source = proj_row[META_COL_PROJ_SOURCE]
        self.extended_paths = {}
        self.counts_paths = {}

        # Check for a clinical file
        self.clinical_path = path_or_none(proj_row, META_COL_PATH_CLINICAL)
        # Check for a samples file
        self.samples_path = path_or_none(proj_row, META_COL_PATH_SAMPLES)
        # Check for a genome events file
        self.genes_path = path_or_none(proj_row, META_COL_PATH_GENES)

        for mut_type in MUT_TYPES:
            # Check for an extended file for the mutation type
            self.extended_paths[mut_type] = path_or_none(proj_row, META_COL_PATH_MUTS_EXTENDED.format(mut_type=mut_type))
        
        for mut_type in MUT_TYPES:
            cat_type = MUT_TYPE_MAP[mut_type]
            # Check for a counts file for the category type
            self.counts_paths[mut_type] = path_or_none(proj_row, META_COL_PATH_MUTS_COUNTS.format(cat_type=cat_type))
    
    # Basic getters
    def get_proj_id(self):
        return self.proj_id
    
    def get_proj_name(self):
        return self.proj_name
    
    def get_oncotree_code(self):
        return self.oncotree_code
    
    def get_oncotree_name(self):
        if self.oncotree_node is not None:
            return self.oncotree_node.name
        return None
    
    def get_oncotree_tissue_code(self):
        if self.oncotree_node is not None:
            return self.oncotree_node.get_tissue_node().code
        return None
    
    def get_proj_num_samples(self):
        try:
            return int(samples_agg_df.loc[self.get_proj_id()]["count"])
        except:
            return 0
    
    def get_proj_source(self):
        return self.proj_source
    
    # Samples file
    def has_samples_df(self):
        return (self.samples_path != None)

    def get_samples_df(self):
        if self.has_samples_df():
            return pd_fetch_tsv(OBJ_DIR, self.samples_path, index_col=1)
        return None
    
    def get_samples_list(self):
        counts_df = pd.DataFrame(index=[], data=[])
        for mut_type in MUT_TYPES:
            if self.has_counts_df(mut_type):
                cat_type_counts_df = self.get_counts_df(mut_type)
                counts_df = counts_df.join(cat_type_counts_df, how='outer')
        
        counts_df = counts_df.fillna(value=0)
        counts_df = counts_df.loc[~(counts_df==0).all(axis=1)]
        return list(counts_df.index.values)
    
    # Clinical file
    def has_clinical_df(self):
        return (self.clinical_path != None)
    
    def get_clinical_df(self):
        if self.has_samples_df() and self.has_clinical_df():
            samples_df = self.get_samples_df()
            samples_df = samples_df.reset_index()
            clinical_df = pd_fetch_tsv(OBJ_DIR, self.clinical_path)
            clinical_df = samples_df.merge(clinical_df, on=PATIENT, how='left')
            clinical_df = clinical_df.fillna(value='nan')
            clinical_df = clinical_df.set_index(SAMPLE)
            return clinical_df
        return None
    
    # Genomic events file
    def has_genes_df(self):
        return (self.genes_path != None)
    
    def get_genes_df(self):
        if self.has_genes_df():
            genes_df = pd_fetch_tsv(OBJ_DIR, self.genes_path)
            return genes_df
        return None
    
    # Counts files
    def has_counts_df(self, mut_type):
        return (self.counts_paths[mut_type] != None)
    
    def get_counts_df(self, mut_type):
        if self.has_counts_df(mut_type):
            counts_df = pd_fetch_tsv(OBJ_DIR, self.counts_paths[mut_type], index_col=0)
            counts_df = counts_df.dropna(how='any', axis='index')
            return counts_df
        return None
    
    # Extended mutation table files
    def has_extended_df(self, mut_type):
        return (self.extended_paths[mut_type] != None)
    
    def get_extended_df(self, mut_type, **kwargs):
        if self.has_extended_df(mut_type):
            return pd_fetch_tsv(OBJ_DIR, self.extended_paths[mut_type], **kwargs)
        return None
    
    def get_sigs_mapping(self):
        proj_sigs_mapping_df = sigs_mapping_df.loc[sigs_mapping_df[META_COL_PROJ] == self.proj_id]
        result = []
        for index, row in proj_sigs_mapping_df.iterrows():
            result.append({
                'sig_group': row[META_COL_SIG_GROUP],
                'oncotree_code': row[META_COL_ONCOTREE_CODE],
                'oncotree_name': tree.find_node(row[META_COL_ONCOTREE_CODE]).name # Assume all codes are valid since this is a computed file
            })
        return result
    

