import requests
import unittest

from constants_for_tests import *

class TestDataListing(unittest.TestCase):

    def test_data_listing(self):
        url = API_BASE + '/data-listing'
        r = requests.post(url)
        r.raise_for_status()
        res = r.json()
        self.assertEqual(['projects', 'sigs', 'sig_per_cancer_type'], list(res.keys()))
        self.assertIn("ICGC-BRCA-EU", list(res['projects'].keys()))
        brca_obj = {
            "name": "Breast ER+ and HER2- Cancer - EU/UK",
            "num_donors": 569,
            "source": "ICGC",
            "has_clinical": True,
            "has_extended": True,
            "has_counts": True
        }
        self.assertEqual(brca_obj, res['projects']['ICGC-BRCA-EU'])
        self.assertIn('SBS', list(res['sigs'].keys()))
        self.assertEqual({'name', 'description', 'index', 'publication'}, set(res['sigs']['SBS'][0].keys()))
        self.assertEqual({'group', 'id', 'cancer-types'}, set(res['sig_per_cancer_type'][0].keys()))
        self.assertEqual({'name', 'id', 'signatures'}, set(res['sig_per_cancer_type'][0]['cancer-types'][0].keys()))
    
