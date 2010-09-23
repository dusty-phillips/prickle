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
    date = DateValidator()
    duration = DurationValidator()
    project = formencode.validators.String(not_empty=True)
    description = formencode.validators.String(not_empty=True)

class ProjectForm(formencode.Schema):
    rate = DecimalValidator()

class InvoiceForm(formencode.Schema):
    date = DateValidator(not_empty=True)
    invoice_number = UniqueInvoiceValidator(not_empty=True)
    bill_to = formencode.validators.String()
    tax = formencode.validators.Number()
