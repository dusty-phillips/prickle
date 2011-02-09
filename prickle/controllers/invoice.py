# Copyright 2010-2011 Dusty Phillips

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

import logging
import datetime
from collections import defaultdict
from decimal import Decimal

from pylons.decorators import validate
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from prickle.lib.base import BaseController, render

from prickle.model.timesheet import Timesheet, Project, Invoice

from prickle.forms.timesheet import InvoiceForm

log = logging.getLogger(__name__)

class InvoiceController(BaseController):

    def create_form(self, id):
        project_name = id
        c.date = datetime.date.today()
        c.project = Project.objects.get(name=project_name)
        c.timesheets = Timesheet.objects(project=c.project,
                __raw__={'invoice': None})
        c.total_time = sum(t.duration for t in c.timesheets)
        c.total_fee = c.total_time * c.project.rate
        c.next_invoice_number = Invoice.next_invoice_number()
        previous_invoices = Invoice.objects(project=c.project)
        if previous_invoices.count():
            c.bill_to = previous_invoices[previous_invoices.count()-1].bill_to
        return render("/invoice/invoice_form.html")

    @validate(schema=InvoiceForm, form='create_form')
    def create(self, id):
        # yes, the swapping of id is confusing, thanks laziness
        # from default routes
        # id = name of the project
        # invoice.id = invoice number
        project_name = id
        project = Project.objects.get(name=project_name)
        invoice = Invoice(
                project=project,
                number=self.form_result['invoice_number'],
                bill_to=self.form_result['bill_to'],
                tax=self.form_result['tax'],
                date=datetime.datetime(
                    self.form_result['date'].year,
                    self.form_result['date'].month,
                    self.form_result['date'].day,
                    ),
                rate=project.rate
                )
        invoice.save()
        timesheets = Timesheet.objects(project=project,
                __raw__={'invoice': None})
        for timesheet in timesheets:
            timesheet.archived_rate = timesheet.rate
            timesheet.invoice = invoice
            timesheet.save()
        return redirect(url(controller="invoice", action="summary",
            id=invoice.number))

    def mark_billed(self, id):
        '''Sometimes we want to record timesheets as invoiced
        without creating an invoice (ie: to clear out unbilled
        stuff or because it was invoiced in another application.

        We do this by attaching those timesheets to a single
        invoice named 'no invoice'.'''
        project_name = id
        project, cr = Project.objects.get_or_create(name=project_name)
        invoice, cr = Invoice.objects.get_or_create(number=-1)

        timesheets = Timesheet.objects(project=project,
                __raw__={'invoice': None})
        for timesheet in timesheets:
            print timesheet
            timesheet.invoice = invoice
            timesheet.save()
        return redirect(url(controller="timesheet", action="index"))

    def view(self, id):
        c.invoice = Invoice.objects.get(number=int(id))
        c.project = c.invoice.project
        c.timesheets = Timesheet.objects(invoice=c.invoice)
        types = defaultdict(int)
        rates = {}
        for timesheet in c.timesheets:
            types[timesheet.type] += timesheet.duration
            rates[timesheet.type] = timesheet.rate
        c.types = {}
        for type, hours in types.items():
            c.types[type] = (hours, rates[type], hours*rates[type])
        c.total_time = sum(t.duration for t in c.timesheets)
        c.total_fee = c.total_time * c.invoice.rate
        c.taxes = c.total_fee * c.invoice.tax * Decimal("0.01")
        c.after_taxes = c.total_fee + c.taxes
        return render("/invoice/invoice.html")

    def list(self):
        c.invoices = Invoice.objects(number__ne=-1)
        return render("/invoice/invoice_list.html")

    def summary(self, id):
        c.invoice = Invoice.objects.get(number=int(id))
        c.timesheets = Timesheet.objects(invoice=c.invoice)
        c.title = "Invoice %s" % id
        c.total_time = sum(t.duration for t in c.timesheets)
        c.total_fee = sum(t.fee for t in c.timesheets)
        c.taxes = c.total_fee * c.invoice.tax * Decimal("0.01")
        c.after_taxes = c.total_fee + c.taxes
        return render('/invoice/invoice_summary.html')
