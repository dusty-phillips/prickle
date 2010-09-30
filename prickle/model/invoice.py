# Copyright 2010 Dusty Phillips

# This file is part of Prickle.

# Prickle is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.

# Prickle is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General
# Public License along with Prickle.  If not, see
# <http://www.gnu.org/licenses/>.

import couchdb

from couchdb.mapping import (Document, DateField, TextField, DecimalField,
        ViewField, IntegerField)
from couchdb.design import ViewDefinition
from pylons import config

prefix = config.get('couchdb_prefix', 'prickle_')

INVOICE_DB = prefix + "invoices"

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
                if (doc._id != "no invoice") {
                    emit(doc.date, doc);
                }
            }''')
    _by_project = ViewField('by_project', '''\
            function(doc) {
                if (doc._id != "no invoice") {
                    emit(doc.project, doc);
                }
            }''')

    def store(self, db=invoices):
        # default database
        super(Invoice, self).store(db)

    @classmethod
    def all_invoices(cls):
        return cls._all_invoices(invoices, descending=True)

    @classmethod
    def for_project(cls, project):
        return cls._by_project(invoices, key=project)

    @classmethod
    def load(cls, id, db=invoices):
        return super(Invoice, cls).load(db, id)

    @classmethod
    def next_invoice_number(cls):
        result = last_invoice_num(invoices)
        if result.rows:
            return result.rows[0]['value'] + 1
        return 1

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

