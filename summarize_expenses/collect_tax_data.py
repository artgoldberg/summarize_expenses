''' Summarize data from multiple transaction spreadsheets
    Expenses are positive and credits are negative
'''
import sys, os.path
import math, argparse
from pprint import pprint
from collections import defaultdict

from obj_tables.io import Reader
import summarize_expenses

'''
class transactions(core.Model):
    # a transaction record
    date = core.DateAttribute()                 # transaction date
    payee = core.StringAttribute()              # recipient of payment
    amount = core.FloatAttribute()              # payment, as a positive dollar amount
    tax_category = core.StringAttribute()       # tax category of payment
    spending_category = core.StringAttribute()  # spending category of payment

    class Meta(core.Model.Meta):
        verbose_name_plural = 'Transactions'

transactions_model = transactions

filename = os.path.join(os.path.dirname(__file__), 'fixtures', 'test_simple.xlsx')
data = obj_tables.io.Reader().run(filename, models=[Transaction], group_objects_by_model=True)
pprint(data)
'''

def clean(l):
    # clean a list of category pattern matches
    return list(filter(lambda y: y!='',
        map(lambda x: x.strip().lower(), l)))

def keep_cat(category, filters, selectors):
    # decide whether category `category` passes through the selectors (to keep) and the filters (to block)
    if selectors:
        for selector in selectors:
            if selector in category.lower():
                return True
        return False
    if filters:
        for filter in filters:
            if filter in category.lower():
                return False
        return True
    return True

def make_parser():
    parser = argparse.ArgumentParser(description="Summarize expenses for taxes and spending planning")
    parser.add_argument('--data_dir', '-d', type=str, help="Directory containing transaction spreadsheets")
    parser.add_argument('--debug', action="store_true", help="Debug, i.e., print all transactions")
    parser.add_argument('--taxes', '-t', action="store_true", help="Output just tax categories")
    parser.add_argument('--select', '-s', type=argparse.FileType('r'),
        help="File with category patterns to select")
    parser.add_argument('--filter', '-f', type=argparse.FileType('r'),
        help="File with category patterns to filter")
    parser.add_argument('files', nargs='*', help="Transaction spreadsheets")
    return parser

def main(args):
    files = args.files
    if args.data_dir:
        print('Data dir:', args.data_dir)
        for file in os.listdir(args.data_dir):
            if file.endswith('.xlsx') and not file.startswith('~'): # only read spreadsheets
                pathname = os.path.join(args.data_dir, file)
                if os.path.isfile(pathname):
                    files.append(pathname)
    if not files:
        raise ValueError('No files provided')

    # read data files
    all_data = {}
    for file in files:
        try:
            data = Reader().run(file, models=[summarize_expenses.schema.Transaction],
                ignore_extra_models=True, 
                ignore_extra_attributes=True, ignore_sheet_order=True, ignore_attribute_order=True)
            data = data[summarize_expenses.schema.Transaction]
            source = os.path.basename(file)
            all_data[source] = data
            print("Read {} records from '{}'".format(len(data), source), file=sys.stderr)
        except ValueError as e:
            print("Error in {}: {}".format(os.path.basename(file), e), file=sys.stderr)
        except Exception as e:
            print("Exception in {}: {}".format(os.path.basename(file), e), file=sys.stderr)

    # read selectors and/or filters
    selectors = []
    if args.select:
        selectors = clean(args.select.readlines())
    filters = []
    if args.filter:
        filters = clean(args.filter.readlines())

    # error check
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

    if args.debug:
        print("source\tdate\tpayee\tamount\ttax category\tspend category")
        for source,transactions in all_data.items():
            for transaction in transactions:
                if args.taxes:
                    if keep_cat(transaction.tax_category, filters, selectors):
                            print("{}\t{}\t{}\t{}\t{}".format(source, transaction.date, transaction.payee,
                                transaction.amount, transaction.tax_category))
                else:
                    if keep_cat(transaction.tax_category, filters, selectors) or \
                       keep_cat(transaction.spending_category, filters, selectors):
                            print("{}\t{}\t{}\t{}\t{}\t{}".format(source, transaction.date, transaction.payee,
                            transaction.amount, transaction.tax_category, transaction.spending_category))

    tax_expenses = defaultdict(float)
    spending_expenses = defaultdict(float)
    num_expenses = 0
    num_credits = 0
    for source,transactions in all_data.items():
        try:
            # Amount may be greater or less than 0
            # positive: expense
            # negative: credit
            sum_expenses = sum([t.amount for t in transactions])
            print("'{}': ${:,.2f} in {} expense and credit transactions".format(source, sum_expenses, len(transactions)))
        except Exception as e:
            print("Error: '{}' {}".format(source, e), file=sys.stderr)
            print('Error found: exiting.', file=sys.stderr)
        for num,transaction in enumerate(transactions, start=1):
            if 0<transaction.amount:
                num_expenses += 1
            else:
                num_credits += 1
            if keep_cat(transaction.tax_category, filters, selectors):
                tax_expenses[cleanup_category(transaction.tax_category)] += transaction.amount
            if keep_cat(transaction.spending_category, filters, selectors):
                spending_expenses[cleanup_category(transaction.spending_category)] += transaction.amount
    print("transactions: {} expense(s) & {} credit(s) in {} source(s)".format(num_expenses, num_credits, len(all_data.keys())))

    # Tax categories:
    print("\n{}\t{}".format('Tax category', 'Total'))
    for tax_category in sorted(tax_expenses.keys()):
        print("{}\t${:,.2f}".format(tax_category, tax_expenses[tax_category]))
    print("TOTAL\t${:,.2f}".format(sum(tax_expenses.values())))

    if not args.taxes:
        # Spending categories:
        print("\n{}\t{}".format('Spending category', 'Total'))
        for spending_category in sorted(spending_expenses.keys()):
            print("{}\t${:,.2f}".format(spending_category, spending_expenses[spending_category]))
        print("TOTAL\t${:,.2f}".format(sum(spending_expenses.values())))

    return (tax_expenses, spending_expenses)

def cleanup_category(category):
    if category=='':
        return 'Not categorized'
    return category.strip().upper()

if __name__ == '__main__':  # pragma: no cover     # reachable only from command line
    try:
        args = make_parser().parse_args()
        main(args)
    except KeyboardInterrupt:
        pass
