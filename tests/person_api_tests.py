import unittest

import responses

from dinaapi.personapi.personapi import PersonAPI


class TestCase(unittest.TestCase):
    @responses.activate
    def personFindTest(self):
        person_api = PersonAPI()
        res = person_api.find("bfa3c68b-8e13-4295-8e25-47dbe041cb64")

        print(res)
