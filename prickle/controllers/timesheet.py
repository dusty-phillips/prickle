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

import logging
import datetime
from collections import defaultdict
from decimal import Decimal

from prickle.forms.timesheet import TimesheetForm

from pylons import request, response, session, tmpl_context as c, url
from pylons.decorators import validate
from pylons.controllers.util import abort, redirect

from prickle.lib.base import BaseController, render

from prickle.model.timesheet import Timesheet, Project, timesheets
from prickle.model.invoice import Invoice


log = logging.getLogger(__name__)

class TimesheetController(BaseController):
    def index(self):
        today = datetime.date.today()
        c.title = "Log Time"
        c.entry_title = "Uninvoiced Entries"
        c.timesheets = Timesheet.all_timesheets(unbilled=True)
        c.total_time = sum(t.duration for t in c.timesheets)
        c.total_fee = sum(t.fee for t in c.timesheets)
        c.project_list = Project.project_list()
        c.date = datetime.date.today()
        c.delete_column = True
        return render('/timesheet/timeform.html')

    @validate(schema=TimesheetForm, form='index')
    def logit(self):
        timesheet = Timesheet(
                date=self.form_result['date'],
                duration=self.form_result['duration'],
                project=self.form_result['project'],
                type=self.form_result['type'],
                description=self.form_result['description'])
        timesheet.store()
        path = request.params.get('next')
        if not path:
            path = url(controller="timesheet", action="index")
        return redirect(path)

    def delete(self, id):
        timesheet = Timesheet.load(id)
        timesheets.delete(timesheet)
        return "deleted"

    def date(self, date):
        c.title = "Log Time for %s" % date
        c.entry_title = "Timesheets for %s" % date
        c.timesheets = Timesheet.for_date(date)
        # Would it be optimal to do this inside couchdb using a reduce function?
        c.total_time = sum(t.duration for t in c.timesheets)
        c.total_fee = sum(t.fee for t in c.timesheets)
        c.date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        c.project_list = Project.project_list()
        return render('/timesheet/timeform.html')

    def month(self, year, month):
        c.date = datetime.date(int(year), int(month), 1)
        c.title = "Timesheet summary for %s" % c.date.strftime("%B, %Y")
        c.timesheets = Timesheet.for_month(year, month)
        c.total_time = sum(t.duration for t in c.timesheets)
        c.total_fee = sum(t.fee for t in c.timesheets)
        c.invoice_column = True
        #FIXME: I'm really tired and suspect this is not the right way to do this
        project_summary = defaultdict(dict) 
        for timesheet in c.timesheets:
            project_summary[timesheet.project]['duration'] = \
                    project_summary[timesheet.project].setdefault(
                            'duration', 0) + timesheet.duration
            project_summary[timesheet.project]['fee'] = \
                    project_summary[timesheet.project].setdefault(
                            'fee', 0) + timesheet.fee

        c.project_summary = project_summary
        return render('/timesheet/month_summary.html')
    
    def project(self, id):
        c.project = Project.load_or_create(id)
        c.timesheets = Timesheet.for_project(id, unbilled=True)
        c.title = "Project Summary for %s" % id
        c.total_time = sum(t.duration for t in c.timesheets)
        c.total_fee = sum(t.fee for t in c.timesheets)
        c.invoices = Invoice.for_project(id)
        return render('/timesheet/project_summary.html')


