import requests
import json
import unittest

from constants_for_tests import *

class TestSignature(unittest.TestCase):

    def test_signature(self):
        url = API_BASE + '/signature'
        
        payload = {
            "name": "COSMIC 1",
            "mut_type": "SBS"
        }
        r = requests.post(url, data=json.dumps(payload))
        r.raise_for_status()
        res = r.json()
        
        self.assertEqual({'data', 'meta'}, set(res.keys()))
        self.assertEqual(96, len(res['data']))
        self.assertEqual(["A[C>A]A", 0.011098326], res['data'][0])

        self.assertEqual({'name', 'description', 'index', 'publication'}, set(res['meta'].keys()))
    
    def test_another_signature(self):
        url = API_BASE + '/signature'
        
        payload = {
            "name": "COSMIC 2",
            "mut_type": "SBS"
        }
        r = requests.post(url, data=json.dumps(payload))
        r.raise_for_status()
        res = r.json()
        
        self.assertEqual(["A[C>A]A", 0.0006827080000000001], res['data'][0])