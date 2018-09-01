import requests
import json
import unittest

from constants_for_tests import *

class TestClustering(unittest.TestCase):

    def test_clustering(self):
        url = API_BASE + '/clustering'
        payload = {
            "projects":["ICGC-BRCA-EU"],
            "signatures":{
                "SBS": [
                    "COSMIC 1",
                    "COSMIC 2",
                    "COSMIC 3",
                    "COSMIC 5",
                    "COSMIC 6",
                    "COSMIC 8",
                    "COSMIC 13",
                    "COSMIC 17",
                    "COSMIC 18",
                    "COSMIC 20",
                    "COSMIC 26",
                    "COSMIC 30"
                ],
                "DBS": [],
                "INDEL": []
            }
        }
        r = requests.post(url, data=json.dumps(payload))
        r.raise_for_status()
        res = r.json()
        self.assertEqual({'name', 'children'}, set(res.keys()))