import requests
import unittest

API_URL = 'http://localhost:8000'

class TestDataListing(unittest.TestCase):

    def test_data_listing(self):
        url = API_URL + '/data-listing'
        r = requests.post(url)
        res = r.json()
        print(res)
        #self.assertEqual(res[''])