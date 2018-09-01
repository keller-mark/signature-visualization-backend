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
            "sample_id": "SA542425"
        }
        r = requests.post(url, data=json.dumps(payload))
        r.raise_for_status()
        decoded_content = r.content.decode('utf-8')

        res = list(csv.reader(decoded_content.splitlines(), delimiter=','))
        self.assertEqual({'chr', 'pos', 'cat', 'mut_dist', 'kataegis'}, set(res[0]))
        
        self.assertEqual(3107, len(res))
    
    def test_rainfall_2(self):
        url = API_BASE + '/kataegis-rainfall'
        payload = {
            "proj_id": "ICGC-COCA-CN",
            "sample_id": "SA602006"
        }
        r = requests.post(url, data=json.dumps(payload))
        r.raise_for_status()
        decoded_content = r.content.decode('utf-8')

        res = list(csv.reader(decoded_content.splitlines(), delimiter=','))
        self.assertEqual({'chr', 'pos', 'cat', 'mut_dist', 'kataegis'}, set(res[0]))
        
        self.assertEqual(129969, len(res))