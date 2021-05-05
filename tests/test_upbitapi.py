import json
import logging
import unittest
from api.upbit import UPBitApi

log = logging.getLogger("mybit")
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())


class SomeTestCase(unittest.TestCase):
    def tearDown(self):
        self.api = UPBitApi()

    def setup(self):
        pass

    def some_test(self):
        res = self.api.get_accounts()
        assert res
        log.info(json.dumps(res, indent=4))
