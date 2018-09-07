import requests
import json
import unittest

from constants_for_tests import *

class TestGenomeEventTrack(unittest.TestCase):

    def test_genome_event_track(self):
        url = API_BASE + '/genome-event-track'
        payload = {
            "projects": ["ICGC-BRCA-EU"],
            "gene_id": "BRCA1"
        }
        r = requests.post(url, data=json.dumps(payload))
        r.raise_for_status()
        res = r.json()
        self.assertEqual(1139, len(res.keys()))
        self.assertEqual({'sample_id', 'proj_id', 'event'}, set(res["SA543682"].keys()))
        self.assertEqual("som_loh", res["SA543682"]["event"])