import requests
import json
import unittest

from constants_for_tests import *

class TestGeneEventTrack(unittest.TestCase):

    def test_gene_event_track(self):
        url = API_BASE + '/plot-gene-event-track'
        payload = {
            "projects": [
                "TCGA-BRCA_BRCA_mc3.v0.2.8.WXS"
            ],
            "gene_id": "BRCA1"
        }
        r = requests.post(url, data=json.dumps(payload))
        r.raise_for_status()
        res = r.json()

        self.assertEqual(1020, len(res))
        self.assertEqual({'sample_id', 'mut_class'}, set(res[0].keys()))
        self.assertEqual("TCGA-BRCA_BRCA_mc3.v0.2.8.WXS TCGA-3C-AAAU-01A-11D-A41F-09", res[0]["sample_id"])
        self.assertEqual("None", res[0]["mut_class"])