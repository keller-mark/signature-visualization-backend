import requests
import unittest

from constants_for_tests import *

class TestDataListing(unittest.TestCase):

    def test_data_listing(self):
        url = API_BASE + '/data-listing'
        r = requests.post(url)
        r.raise_for_status()
        res = r.json()
        self.assertEqual(['sources', 'sigs', 'sig_presets'], list(res.keys()))
        self.assertIn("ICGC-BRCA-EU", list(res['sources'].keys()))
        brca_obj = {
            "name": "Breast ER+ and HER2- Cancer - EU/UK",
            "num_donors": 569,
            "source": "ICGC",
            "has_clinical": True,
            "has_ssm": True,
            "has_counts": True
        }
        self.assertEqual(brca_obj, res['sources']['ICGC-BRCA-EU'])
        self.assertEqual({'name', 'description', 'index', 'publication'}, set(res['sigs'][0].keys()))
        self.assertEqual({'group', 'id', 'cancer-types'}, set(res['sig_presets'][0].keys()))
        self.assertEqual({'name', 'id', 'signatures'}, set(res['sig_presets'][0]['cancer-types'][0].keys()))
    
