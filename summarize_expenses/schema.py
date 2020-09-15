# Schema automatically generated at 2019-09-24 19:47:09

import obj_tables


class Transaction(obj_tables.Model):
    """ Stores transactions """

    date = obj_tables.DateAttribute(verbose_name='Date')
    amount = obj_tables.FloatAttribute(verbose_name='Amount')
    tax_category = obj_tables.StringAttribute(verbose_name='Tax category')
    payee = obj_tables.LongStringAttribute(verbose_name='Payee')
    spending_category = obj_tables.StringAttribute(verbose_name='Spending category')

    class Meta(obj_tables.Model.Meta):
        table_format = obj_tables.TableFormat.row
        attribute_order = ('date', 'amount', 'tax_category', 'payee', 'spending_category',)
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transaction'
        description = 'Stores transactions'
