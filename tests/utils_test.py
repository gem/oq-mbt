

import unittest
from mbt.utils import mag_to_mo

class MagToMoTestCase(unittest.TestCase):

    def testcase01(self):
        magnitude = 6.0
        computed = mag_to_mo(6.0)
        expected = 1.2589254117942e+18
        self.assertLess(abs(computed-expected), 1e5)
