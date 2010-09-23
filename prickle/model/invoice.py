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
    _by_project = ViewField('by_project', '''\
            function(doc) {
                emit(doc.project, doc);
            }''')

    def store(self, db=invoices):
        # default database
        super(Invoice, self).store(db)

    @classmethod
    def all_invoices(cls):
        return cls._all_invoices(invoices)

    @classmethod
    def for_project(cls, project):
        return cls._by_project(invoices, key=project)

    @classmethod
    def load(cls, id, db=invoices):
        return super(Invoice, cls).load(db, id)

    @classmethod
    def next_invoice_number(cls):
        return last_invoice_num(invoices).rows[0]['value'] + 1

last_invoice_num = ViewDefinition("last_num", "all", '''\
    function(doc) {
        emit(1, parseInt(doc._id));
    }''',
    '''\
    function(keys, values, rereduce) {
        var max = 0;
        for (var i in values) {
            if (values[i] > max) {
                max = values[i];
            }
        }
        return max;
    }''')
last_invoice_num.sync(invoices)
Invoice._all_invoices.sync(invoices)
Invoice._by_project.sync(invoices)

