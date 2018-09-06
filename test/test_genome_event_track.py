import requests
import json
import unittest

from constants_for_tests import *

class TestGenomeEventTrack(unittest.TestCase):

    def test_exposures(self):
        url = API_BASE + '/genome-event-track'
        payload = {
            "projects": ["ICGC-BRCA-EU"],
            "gene_id": "BRCA1"
        }
        r = requests.post(url, data=json.dumps(payload))
        r.raise_for_status()
        res = r.json()
        self.assertEqual(569, len(res.keys()))
        self.assertEqual({'donor_id', 'proj_id', 'event'}, set(res["DO217786"].keys()))
        self.assertEqual("8", res["DO217786"]["event"])