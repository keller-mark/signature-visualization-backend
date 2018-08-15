import requests
import json
import unittest

from constants_for_tests import *

class TestKataegis(unittest.TestCase):

    def test_kataegis(self):
        url = API_BASE + '/kataegis'
        
        payload = {
            "sources":[
                "ICGC-BRCA-EU"
            ]
        }
        r = requests.post(url, data=json.dumps(payload))
        r.raise_for_status()
        res = r.json()
        self.assertEqual(569, len(res.keys()))
        self.assertEqual(4, len(res['DO217786']['kataegis']['1']))