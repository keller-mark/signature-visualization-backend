from web_constants import *

def match_proj_to_sigs(proj_data, sig_group):
    match_df = pd.DataFrame(index=[], columns=['Signature Group', 'Project', 'Oncotree Code'])
    sig_group_df = pd.read_csv(join(OBJ_DIR, META_SIGS_FILENAME), sep='\t', index_col=0)
    sig_group_df = 
