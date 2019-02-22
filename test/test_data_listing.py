import requests
import unittest

from constants_for_tests import *

""" All JSON objects should look how we expect """

class TestDataListing(unittest.TestCase):

    def test_data_listing(self):
        url = API_BASE + '/data-listing'
        r = requests.post(url)
        r.raise_for_status()
        res = r.json()

        toplevel_keys = {
            'projects', 
            'signatures', 
            'cancer_type_map', 
            'tissue_types', 
            'tricounts_methods'
        }
        self.assertEqual(toplevel_keys, set(res.keys()))

        project_keys = {
            'id',
            'name',
            'num_samples',
            'source',
            'has_clinical',
            'has_gene_mut',
            'has_gene_exp',
            'has_gene_cna',
            'sigs_mapping',
            'oncotree_code',
            'oncotree_name',
            'oncotree_tissue_code'
        }
        sigs_mapping_keys = {
            'sig_group',
            'oncotree_code',
            'oncotree_name'
        }
        for project in res['projects']:
            self.assertEqual(project_keys, set(project.keys()))
            for sigs_mapping in project['sigs_mapping']:
                self.assertEqual(sigs_mapping_keys, set(sigs_mapping.keys()))
        
        sigs_keys = {
            'id',
            'group',
            'publication',
            'description',
            'index',
            'cat_type',
            'mut_type'
        }
        for sig in res['signatures']:
            self.assertEqual(sigs_keys, set(sig.keys()))
        
        cancer_type_map_keys = {
            'group',
            'cancer_type',
            'oncotree_code',
            'oncotree_name',
            'signature'
        }
        for cancer_type_map in res['cancer_type_map']:
            self.assertEqual(cancer_type_map_keys, set(cancer_type_map.keys()))

        tissue_type_keys = {
            'oncotree_code',
            'oncotree_name'
        }
        for tissue_type in res['tissue_types']:
            self.assertEqual(tissue_type_keys, set(tissue_type.keys()))
    
