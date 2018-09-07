import requests
import json
import unittest

from constants_for_tests import *

class TestExposuresSingleDonor(unittest.TestCase):

    def test_exposures_single_donor(self):
        url = API_BASE + '/exposures-single-sample'
        payload = {
            "sample_id": "SA557034", 
            "proj_id": "ICGC-BRCA-EU", 
            "signatures":{
                "SBS": [
                    "COSMIC 1",
                    "COSMIC 2",
                    "COSMIC 3",
                    "COSMIC 4",
                    "COSMIC 5",
                    "COSMIC 6",
                    "COSMIC 7",
                    "COSMIC 8",
                    "COSMIC 9",
                    "COSMIC 10",
                    "COSMIC 11",
                    "COSMIC 12",
                    "COSMIC 13",
                    "COSMIC 14",
                    "COSMIC 15",
                    "COSMIC 16",
                    "COSMIC 17",
                    "COSMIC 18",
                    "COSMIC 19",
                    "COSMIC 20",
                    "COSMIC 21",
                    "COSMIC 22",
                    "COSMIC 23",
                    "COSMIC 24",
                    "COSMIC 25",
                    "COSMIC 26",
                    "COSMIC 27",
                    "COSMIC 28",
                    "COSMIC 29",
                    "COSMIC 30",
                    "5* A"
                ],
                "DBS": [],
                "INDEL": []
            }
        }
        r = requests.post(url, data=json.dumps(payload))
        r.raise_for_status()
        res = r.json()
        self.assertEqual(1, len(res))
        self.assertEqual({'sample_id', 'proj_id', 'exposures', 'clinical'}, set(res[0].keys()))
        self.assertEqual({'SBS', 'DBS', 'INDEL'}, set(res[0]['exposures'].keys()))
        self.assertEqual(31, len(res[0]['exposures']['SBS']))