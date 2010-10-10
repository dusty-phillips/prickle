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

import formencode

import couchdb


from .validators import DateValidator, DurationValidator, DecimalValidator

from prickle.model.invoice import invoices

class UniqueInvoiceValidator(formencode.validators.FancyValidator):
    def _to_python(self, value, state):
        try:
            number = invoices[value]
        except couchdb.http.ResourceNotFound:
            return value
        else:
            raise formencode.validators.Invalid("Duplicate invoice id")

class TimesheetForm(formencode.Schema):
    next = formencode.validators.String()
    date = DateValidator()
    duration = DurationValidator(not_empty=True)
    project = formencode.validators.String(not_empty=True)
    type = formencode.validators.String()
    description = formencode.validators.String()

class ProjectForm(formencode.Schema):
    rate = DecimalValidator()

class InvoiceForm(formencode.Schema):
    date = DateValidator(not_empty=True)
    invoice_number = UniqueInvoiceValidator(not_empty=True)
    bill_to = formencode.validators.String()
    tax = formencode.validators.Number()
