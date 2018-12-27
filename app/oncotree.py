import json

class OncoNode():

    def __init__(self, node_json, parent):
        self.code = node_json['code']
        self.name = node_json['name']
        #self.main_type = node_json['mainType']
        self.tissue = node_json['tissue']
        self.level = node_json['level']
        self.parent = parent
        self.children = []
        for child in node_json['children'].values():
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

    # From a child/leaf node, go up the tree to the tissue type node, 
    # which should be the one below the TISSUE root node
    def get_tissue_node(self):
        def get_tissue_type_aux(node):
            if node.parent == None:
                return None # only would happen if you ask for tissue on the head node
            if node.parent.code == "TISSUE":
                return node
            return get_tissue_type_aux(node.parent)
        return get_tissue_type_aux(self)


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
    
    def get_tissue_nodes(self):
        return self.head.children