'''
sum tax category data:
    define schema for transactions_2016, with amount and 'Tax category'
    ensure that spreadsheets contain those columns, and that all expenses are positive
    for each spreadsheet, load amounts & tax categories
    sum amounts across tax categories
'''
    
import sys, os.path
import math, argparse
from collections import defaultdict
from obj_model import core
from obj_model.io import Reader


class transactions(core.Model):
    amount = core.FloatAttribute()
    tax_category = core.StringAttribute()
    spending_category = core.StringAttribute()

    class Meta(core.Model.Meta):
        verbose_name_plural = 'Transactions'

def main(transactions):
    parser = argparse.ArgumentParser(description="Summarize expenses for taxes and spending planning")
    parser.add_argument('--data_dir', '-d', type=str, help="Directory containing transaction spreadsheets")
    parser.add_argument('files', nargs='*', help="Transaction spreadsheets")
    args = parser.parse_args()
    files = args.files
    if args.data_dir:
        for file in os.listdir(args.data_dir):
            if file.endswith('.xlsx') and not file.startswith('~'): # only read spreadsheets
                pathname = os.path.join(args.data_dir, file)
                if os.path.isfile(pathname):
                    files.append(pathname)
    if not files:
        raise ValueError('No files provided')
    all_data = {}
    for file in files:
        try:
            data = Reader().run(file, [transactions],
                ignore_other_sheets=True, ignore_extra_attributes=True)
            source = file.split('.')[0]
            all_data[source] = data[transactions]
            print("Read {} records from '{}'".format(len(data[transactions]), source),
                file=sys.stderr)
        except Exception as e:
            print("Error: {}".format(e), file=sys.stderr)

    errors = []
    for source,transactions in all_data.items():
        for num,transaction in enumerate(transactions, start=1):
            if math.isnan(transaction.amount):
                errors.append("Error: amount is NaN: '{}':{}: '{}' '{}'".format(source,
                    num, transaction.amount, transaction.tax_category))
    if errors:
        print('source transaction_num transaction.amount transaction.tax_category', file=sys.stderr)
        for error in errors:
            print(error, file=sys.stderr)
        print('Errors found: exiting.', file=sys.stderr)
        return

    tax_expenses = defaultdict(float)
    spending_expenses = defaultdict(float)
    for source,transactions in all_data.items():
        try:
            print("'{}': ${:,.2f} in {} transactions".format(source,
                sum([t.amount for t in transactions]), len(transactions)))
        except Exception as e:
            print("Error: '{}' {}".format(source, e), file=sys.stderr)
            print('Error found: exiting.', file=sys.stderr)
        for num,transaction in enumerate(transactions, start=1):
            tax_expenses[cleanup_category(transaction.tax_category)] += transaction.amount
            spending_expenses[cleanup_category(transaction.spending_category)] += transaction.amount
    # Tax categories:
    print("\n{}\t{}".format('Tax category', 'Total'))
    for tax_category in sorted(tax_expenses.keys()):
        print("{}\t${:,.0f}".format(tax_category, tax_expenses[tax_category]))
    # Spending categories:
    print("\n{}\t{}".format('Spending category', 'Total'))
    for spending_category in sorted(spending_expenses.keys()):
        print("{}\t${:,.0f}".format(spending_category, spending_expenses[spending_category]))

def cleanup_category(category):
    if category=='':
        return 'Not categorized'
    return category.strip().upper()

main(transactions)
