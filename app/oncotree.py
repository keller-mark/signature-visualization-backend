import json
from web_constants import *
from helpers import *

from sig_data import *
from project_data import *

sigs = get_all_sig_data()
projs = get_all_project_data()

class OncoNode():

    def __init__(self, node_json, parent):
        self.code = node_json['code']
        self.name = node_json['name']
        #self.main_type = node_json['mainType']
        self.tissue = node_json['tissue']
        self.level = node_json['level']
        self.parent = parent
        self.children = []
        for child_code, child in node_json['children'].items():
            self.children.append(OncoNode(child, self))
    
    # From a list of oncotree codes, go up the tree to find the closest ancestor to this node that is in the list
    # Used to match a specific project's oncotree code to the list of signature oncotree code mappings
    def find_closest_parent(self, code_list):
        def find_closest_parent_aux(node):
            if node == None:
                return None
            if node.parent == None:
                return None
            if node.code in code_list:
                return node
            return find_closest_parent_aux(node.parent)
        return find_closest_parent_aux(self)


class OncoTree():

    def __init__(self, tree_json):
        self.head = OncoNode(tree_json['TISSUE'], None)
    
    def find_node(self, code):
        def find_node_aux(node):
            if node == None:
                return None
            if node.code == code:
                return node
            for child in node.children:
                found = find_node_aux(child)
                if found is not None:
                    return found
            return None
        return find_node_aux(self.head)
    
    
        
            
        

with open(ONCOTREE_FILE) as f:
    tree_json = json.load(f)
    tree = OncoTree(tree_json)

    print(tree.find_node('CHRCC').find_closest_parent(['BRCA', 'CCRCC']).code)



def match_proj_to_sigs(proj_data, sig_group):
    match_df = pd.DataFrame(index=[], data=[], columns=[META_COL_SIG_GROUP, META_COL_PROJ, META_COL_ONCOTREE_CODE])
    


