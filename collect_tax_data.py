'''
sum tax category data:
    define schema for transactions_2016, with amount and 'Tax category'
    ensure that spreadsheets contain those columns, and that all expenses are positive
    for each spreadsheet, load amounts & tax categories
    sum amounts across tax categories
'''
    
DATA_DIRECTORY = '/Users/arthur_at_sinai/Dropbox/Arthur/PersonalOnDropbox/Financial/Taxes2016/Categorized expenses'

FILES = [
    'AmEx Transactions 01_27 to 12_31 2016.xlsx',
    '''
    'Amazon_2016.xlsx',
    'Capital One 2016 transactions MG.xlsx',
    'Chase3909_for_2016 MG.xlsx',
    'IAG - USAlliance - 2016 Transactions MG.xlsx',
    'MasterCard_2016 MG.xlsx',
    'NYU_FCU.xlsx',
    'Vanguard LLC Transactions.xlsx',
    '''
    ]

import sys, os.path
import math
from collections import defaultdict
from wc_utils.schema import core, utils
from wc_utils.schema.io import Reader

class transactions_2016(core.Model):
    amount = core.FloatAttribute()
    tax_category = core.StringAttribute()

    class Meta(core.Model.Meta):
        verbose_name_plural = 'Transactions 2016'

def main():
    all_data = {}
    for file in FILES:
        try:
            data = Reader().run(os.path.join(DATA_DIRECTORY, file),[transactions_2016],
                ignore_other_sheets=True, skip_missing_attributes=True)
            source = file.split('.')[0]
            all_data[source] = data[transactions_2016]
            #print("Read {} records from '{}'".format(len(data[transactions_2016]), source))
        except Exception as e:
            print("Error: {}".format(e), file=sys.stderr)
    
    total_expenses = defaultdict(float)
    for source,transactions in all_data.items():
        for num,transaction in enumerate(transactions, start=1):
            if math.isnan(transaction.amount):
                print("Error: amount is NaN: '{}':{}, {}".format(source, num, transaction.tax_category),
                    file=sys.stderr)
        
    for source,transactions in all_data.items():
        try:
            print("'{}': {} in {} transactions".format(source,
                int(sum([t.amount for t in transactions])), len(transactions)))
        except Exception as e:
            print("Error: '{}' {}".format(source, e), file=sys.stderr)
        # print("Num\tSource\tCategory\tAmount")
        for num,transaction in enumerate(transactions, start=1):
            category = transaction.tax_category.strip().upper()
            # print("{},{},{},{}".format(num, source, category, transaction.amount))
            total_expenses[category] += transaction.amount
    print("{}\t{}\tUsed".format('Tax category', 'Total'))
    for tax_category in sorted(total_expenses.keys()):
        print("{}\t{}".format(tax_category, int(total_expenses[tax_category])))

main()