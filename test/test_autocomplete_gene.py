import requests
import json
import unittest

from constants_for_tests import *

class TestAutocompleteGene(unittest.TestCase):

    def test_autocomplete_gene(self):
        url = API_BASE + '/autocomplete-gene'
        payload = {
            "gene_id_partial": "BR",
            "projects": [
                "TCGA-BRCA_BRCA_mc3.v0.2.8.WXS"
            ]
        }
        r = requests.post(url, data=json.dumps(payload))
        r.raise_for_status()
        res = r.json()
        
        self.assertIn("BRCA1", res)
        self.assertIn("BRCA2", res)