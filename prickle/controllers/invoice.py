import logging
import datetime
from decimal import Decimal

from pylons.decorators import validate
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from prickle.lib.base import BaseController, render

from prickle.model.invoice import Invoice
from prickle.model.timesheet import Timesheet, Project

from prickle.forms.timesheet import InvoiceForm

log = logging.getLogger(__name__)

class InvoiceController(BaseController):

    def create_form(self, id):
        project_name = id
        c.date = datetime.date.today()
        c.project = Project.load_or_create(project_name)
        c.timesheets = Timesheet.for_project(project_name, unbilled=True)
        c.total_time = sum(t.duration for t in c.timesheets)
        c.total_fee = c.total_time * c.project.rate
        c.next_invoice_number = Invoice.next_invoice_number()
        previous_invoices = Invoice.for_project(project_name)
        if previous_invoices.rows:
            c.bill_to = previous_invoices.rows[-1].bill_to
        return render("/invoice_form.html")

    @validate(schema=InvoiceForm, form='create_form')
    def create(self, id):
        # yes, the swapping of id is confusing, thanks laziness
        # from default routes
        # id = name of the project
        # invoice.id = invoice number
        project_name = id
        project = Project.load_or_create(project_name)
        invoice = Invoice(
                project=project_name,
                id=self.form_result['invoice_number'],
                bill_to=self.form_result['bill_to'],
                tax=self.form_result['tax'],
                date=self.form_result['date'],
                rate=project.rate
                )
        invoice.store()
        timesheets = Timesheet.for_project(project_name, unbilled=True)
        for timesheet in timesheets:
            timesheet.invoice = invoice.id
            timesheet.store()
        return redirect(url(controller="invoice", action="summary",
            id=invoice.id))

    def view(self, id):
        invoice = Invoice.load(id)
        c.invoice = invoice
        c.project = Project.load_or_create(invoice.project)
        c.timesheets = Timesheet.for_invoice(id)
        c.total_time = sum(t.duration for t in c.timesheets)
        c.total_fee = c.total_time * invoice.rate
        c.taxes = c.total_fee * invoice.tax * Decimal("0.01")
        c.after_taxes = c.total_fee + c.taxes
        return render("/invoice.html")

    def list(self):
        c.invoices = Invoice.all_invoices()
        return render("/invoice_list.html")

    def summary(self, id):
        c.timesheets = Timesheet.for_invoice(id)
        c.title = "Invoice %s" % id
        c.total_time = sum(t.duration for t in c.timesheets)
        c.total_fee = sum(t.fee for t in c.timesheets)
        c.invoice = Invoice.load(id)
        c.taxes = c.total_fee * c.invoice.tax * Decimal("0.01")
        c.after_taxes = c.total_fee + c.taxes
        return render('/invoice_summary.html')
