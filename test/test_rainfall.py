import requests
import json
import csv
import unittest

from constants_for_tests import *

class TestRainfall(unittest.TestCase):

    def test_rainfall(self):
        url = API_BASE + '/kataegis-rainfall'
        
        payload = {
            "proj_id": "ICGC-BRCA-EU",
            "donor_id": "DO217786"
        }
        r = requests.post(url, data=json.dumps(payload))
        r.raise_for_status()
        decoded_content = r.content.decode('utf-8')

        res = list(csv.reader(decoded_content.splitlines(), delimiter=','))
        self.assertEqual({'chr', 'pos', 'cat', 'cat_index', 'mut_dist', 'kataegis'}, set(res[0]))
        
        self.assertEqual(3107, len(res))