import couchdb

from couchdb.mapping import (Document, DateField, TextField, DecimalField,
        ViewField, IntegerField)
from couchdb.design import ViewDefinition

INVOICE_DB = "prickle_invoices"

couch = couchdb.Server()

try:
    invoices = couch[INVOICE_DB]
except couchdb.http.ResourceNotFound:
    invoices = couch.create(INVOICE_DB)

class Invoice(Document):
    date = DateField()
    bill_to = TextField()
    project = TextField()
    rate = DecimalField()
    tax = DecimalField(default=0.0)

    _all_invoices = ViewField('invoices', '''\
            function(doc) {
                emit(doc.id, doc);
            }''')

    def store(self, db=invoices):
        # default database
        super(Invoice, self).store(db)

    @classmethod
    def all_invoices(cls):
        return cls._all_invoices(invoices)

    @classmethod
    def load(cls, id, db=invoices):
        return super(Invoice, cls).load(db, id)

Invoice._all_invoices.sync(invoices)
