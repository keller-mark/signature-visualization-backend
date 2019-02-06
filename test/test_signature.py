import requests
import json
import unittest

from constants_for_tests import *

class TestSignature(unittest.TestCase):

    def test_signature_sbs(self):
        url = API_BASE + '/plot-signature'
        
        payload = {
            "signature": "COSMIC 1",
            "mut_type": "SBS"
        }
        r = requests.post(url, data=json.dumps(payload))
        r.raise_for_status()
        res = r.json()

        self.assertEqual(96, len(res))

        obj_keys = {
            'cat_SBS',
            'probability'
        }

        for obj in res:
            self.assertEqual(obj_keys, set(obj.keys()))

        self.assertAlmostEqual(0.011098326, res[0]['probability'])
        self.assertAlmostEqual('A[C>A]A', res[0]['cat_SBS'])

    
    def test_signature_dbs(self):
        url = API_BASE + '/plot-signature'
        
        payload = {
            "signature": "PCAWG DBS1",
            "mut_type": "DBS"
        }
        r = requests.post(url, data=json.dumps(payload))
        r.raise_for_status()
        res = r.json()
        
        self.assertEqual(78, len(res))

        obj_keys = {
            'cat_DBS',
            'probability'
        }

        for obj in res:
            self.assertEqual(obj_keys, set(obj.keys()))

        self.assertAlmostEqual(0.000049700, res[0]['probability'])
        self.assertAlmostEqual('AC>CA', res[0]['cat_DBS'])
    
    def test_signature_indel(self):
        url = API_BASE + '/plot-signature'
        
        payload = {
            "signature": "PCAWG ID1",
            "mut_type": "INDEL"
        }
        r = requests.post(url, data=json.dumps(payload))
        r.raise_for_status()
        res = r.json()
        
        self.assertEqual(83, len(res))

        obj_keys = {
            'cat_INDEL',
            'probability'
        }

        for obj in res:
            self.assertEqual(obj_keys, set(obj.keys()))

        self.assertAlmostEqual(0.000159889, res[0]['probability'])
        self.assertAlmostEqual('DEL_C_1_0', res[0]['cat_INDEL'])