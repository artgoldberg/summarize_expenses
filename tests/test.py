"""
:Author: Arthur Goldberg <Arthur.Goldberg@mssm.edu>
"""

import sys
import os
import unittest
import tempfile

import collect_tax_data


# Namespace(data_dir=None, debug=False, files=['data/Amazon_joint_2018.xlsx'], filter=None, select=None, taxes=False)
class Test(unittest.TestCase):

    DATA_FILENAME = os.path.join(os.path.dirname(__file__), 'fixtures', 'test_expense_data.xlsx')

    def test(self):
        self.assertTrue(True)
        print(self.DATA_FILENAME)
        