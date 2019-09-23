"""
:Author: Arthur Goldberg <Arthur.Goldberg@mssm.edu>
"""

import sys
import os
import unittest
import tempfile
from argparse import Namespace
from pprint import pprint

import collect_tax_data


class Test(unittest.TestCase):

    FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')
    DATA_FILENAME = os.path.join(FIXTURES, 'test_expense_data.xlsx')
    SELECTORS = os.path.join(FIXTURES, 'selectors.txt')
    FILTERS = os.path.join(FIXTURES, 'filters.txt')

    def test(self):
        print()
        args = Namespace(data_dir=None, debug=False, files=[self.DATA_FILENAME], filter=None,
            select=None, taxes=False)
        tax_expenses, spending_expenses = collect_tax_data.main(args)
        expected_tax_expenses = \
            {'MEIRA C: REPAIRS AND MAINTENANCE': 160.0,
                'NO TAX CONSEQUENCES': 40.0,
                'OTHER': 1.0,
                'NONE: POLITICAL': 80.0}
        self.assertEqual(expected_tax_expenses, tax_expenses)
        args = Namespace(data_dir=self.FIXTURES, debug=False, files=[], filter=None,
            select=None, taxes=False)
        tax_expenses, spending_expenses = collect_tax_data.main(args)

        with open(self.SELECTORS, 'r') as selector:
            args = Namespace(data_dir=None, debug=False, files=[self.DATA_FILENAME], filter=None,
                select=selector, taxes=False)
            tax_expenses, _ = collect_tax_data.main(args)
            self.assertEqual({'MEIRA C: REPAIRS AND MAINTENANCE': 160.0}, tax_expenses)

        with open(self.FILTERS, 'r') as filter:
            args = Namespace(data_dir=None, debug=False, files=[self.DATA_FILENAME], filter=filter,
                select=None, taxes=False)
            tax_expenses, _ = collect_tax_data.main(args)
            self.assertEqual({'MEIRA C: REPAIRS AND MAINTENANCE': 160.0}, tax_expenses)

        args = Namespace(data_dir=None, debug=False, files=[], filter=None, select=None, taxes=False)
        with self.assertRaises(ValueError):
            collect_tax_data.main(args)
