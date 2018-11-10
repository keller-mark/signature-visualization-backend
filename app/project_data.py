import pandas as pd
from web_constants import *

# Helper function
def path_or_none(proj_row, index):
    if pd.notnull(proj_row[index]):
        return proj_row[index]
    return None

# Easy loading of TSV files with pandas
def pd_fetch_tsv(s3_key, **kwargs):
    filepath = os.path.join(OBJ_DIR, s3_key)
    return pd.read_csv(filepath, sep='\t', **kwargs)

""" Load the metadata file to be able to create ProjectData objects """
meta_df = pd.read_csv(DATA_META_FILE, sep='\t', index_col=0)
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
        return {
            "id": obj.get_proj_id(),
            "name": obj.get_proj_name(),
            "num_donors": obj.get_proj_num_donors(),
            "source": obj.get_proj_source(),
            "has_clinical": obj.has_clinical_df(),
            "has_extended": obj.has_all_extended_dfs(),
            "has_counts": obj.has_all_counts_dfs()
        }
    return list(map(project_data_to_json, get_all_project_data()))


""" 
Class representing a single row of the DATA_META_FILE, 
also how the files referenced within the meta file should be loaded into data frames
"""
class ProjectData():
    
    def __init__(self, proj_id, proj_row):
        self.proj_id = proj_id
        self.proj_name = proj_row['name']
        self.proj_num_donors = proj_row['num_donors']
        self.proj_source = proj_row['source']
        self.extended_paths = {}
        self.counts_paths = {}

        # Check for a clinical file
        self.clinical_path = path_or_none(proj_row, 'path_clinical')
        # Check for a samples file
        self.samples_path = path_or_none(proj_row, 'path_samples')
        # Check for a genome events file
        self.events_path = path_or_none(proj_row, 'path_genes')

        for mut_type in SIG_TYPES.keys():
            # Check for an extended file for the mutation type
            self.extended_paths[mut_type] = path_or_none(proj_row, 'path_extended_' + mut_type)
            # Check for a counts file for the mutation type
            self.counts_paths[mut_type] = path_or_none(proj_row, 'path_counts_' + mut_type)
    
    # Basic getters
    def get_proj_id(self):
        return self.proj_id
    
    def get_proj_name(self):
        return self.proj_name
    
    def get_proj_num_donors(self):
        return self.proj_num_donors
    
    def get_proj_source(self):
        return self.proj_source
    
    # Samples file
    def has_samples_df(self):
        return (self.samples_path != None)

    def get_samples_df(self):
        if self.has_samples_df():
            return pd_fetch_tsv(self.samples_path, index_col=1)
        return None
    
    def get_samples_list(self):
        if self.has_samples_df():
            samples_df = self.get_samples_df()
            return list(samples_df.index.values)
        return None
    
    # Clinical file
    def has_clinical_df(self):
        return (self.clinical_path != None)
    
    def get_clinical_df(self):
        if self.has_samples_df() and self.has_clinical_df():
            samples_df = self.get_samples_df()
            samples_df = samples_df.reset_index()
            clinical_df = pd_fetch_tsv(self.clinical_path)
            clinical_df = samples_df.merge(clinical_df, on=PATIENT, how='left')
            clinical_df = clinical_df.fillna(value='nan')
            clinical_df = clinical_df.set_index(SAMPLE)
            return clinical_df
        return None
    
    # Genomic events file
    def has_events_df(self):
        return (self.events_path != None)
    
    def get_events_df(self):
        if self.has_events_df():
            events_df = pd_fetch_tsv(self.events_path)
            return events_df
        return None
    
    # Counts files
    def has_counts_df(self, mut_type):
        return (self.counts_paths[mut_type] != None)
    
    def has_all_counts_dfs(self):
        has_all = True
        for mut_type in SIG_TYPES.keys():
            has_all = has_all and self.has_counts_df(mut_type)
        return has_all
    
    def get_counts_df(self, mut_type):
        if self.has_counts_df(mut_type):
            counts_df = pd_fetch_tsv(self.counts_paths[mut_type], index_col=0)
            counts_df = counts_df.dropna(how='any', axis='index')
            return counts_df
        return None
    
    # Extended mutation table files
    def has_extended_df(self, mut_type):
        return (self.extended_paths[mut_type] != None)
    
    def has_all_extended_dfs(self):
        has_all = True
        for mut_type in SIG_TYPES.keys():
            has_all = has_all and self.has_extended_df(mut_type)
        return has_all
    
    def get_extended_df(self, mut_type, **kwargs):
        if self.has_extended_df(mut_type):
            return pd_fetch_tsv(self.extended_paths[mut_type], **kwargs)
        return None
    

