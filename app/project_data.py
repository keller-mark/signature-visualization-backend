import pandas as pd
from web_constants import *

def path_or_none(proj_row, index):
    if pd.notnull(proj_row[index]):
        return proj_row[index]
    return None

def pd_fetch_tsv(s3_key, **kwargs):
    filepath = os.path.join(OBJ_DIR, s3_key)
    return pd.read_csv(filepath, sep='\t', **kwargs)

meta_df = pd.read_csv(DATA_META_FILE, sep='\t', index_col=0)
def get_project_data(proj_id):
    return ProjectData(meta_df.loc[proj_id])

def get_all_project_data():
    rows = meta_df.to_json(orient='records')
    return list(map(lambda row: ProjectData(row), rows))

class ProjectData():
    
    def __init__(self, proj_row):
        self.proj_id = proj_row['id']
        self.extended_paths = {}
        self.counts_paths = {}

        # Check for a clinical file
        self.clinical_path = path_or_none(proj_row, 'path_clinical')
        # Check for a samples file
        self.samples_path = path_or_none(proj_row, 'path_samples')

        for mut_type in SIG_TYPES.keys():
            # Check for an extended file for the mutation type
            self.extended_paths[mut_type] = path_or_none(proj_row, 'path_extended_' + mut_type)
            # Check for a counts file for the mutation type
            self.counts_paths[mut_type] = path_or_none(proj_row, 'path_counts_' + mut_type)
    
    def get_proj_id(self):
        return self.proj_id
    
    def has_samples_df(self):
        return (self.samples_path != None)

    def get_samples_df(self):
        if self.has_samples_df():
            return pd_fetch_tsv(self.samples_path, index_col=1)
        return None
    
    def has_clinical_df(self):
        return (self.clinical_path != None)
    
    def get_clinical_df(self):
        if self.has_samples_df() and self.has_clinical_df():
            samples_df = self.get_samples_df()
            clinical_df = pd_fetch_tsv(self.clinical_path)
            clinical_df = samples_df.merge(clinical_df, on=PATIENT, how='left')
            clinical_df = clinical_df.fillna(value='nan')
            clinical_df = clinical_df.set_index(SAMPLE)
            return clinical_df
        return None
    
    def has_counts_df(self, mut_type):
        return (self.counts_paths[mut_type] != None)
    
    def get_counts_df(self, mut_type):
        if self.has_counts_df(mut_type):
            counts_df = pd_fetch_tsv(self.counts_paths[mut_type], index_col=0)
            counts_df = counts_df.dropna(how='any', axis='index')
            return counts_df
        return None
    
    def has_extended_df(self, mut_type):
        return (self.extended_paths[mut_type] != None)
    
    def get_extended_df(self, mut_type):
        if self.has_extended_df(mut_type):
            return pd_fetch_tsv(self.extended_paths[mut_type])
        return None
    

