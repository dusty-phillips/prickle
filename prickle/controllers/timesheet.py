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
from dateutil.relativedelta import relativedelta
import json
from collections import defaultdict
from decimal import Decimal

from prickle.forms.timesheet import TimesheetForm, EditTimesheetForm

from pylons import request, response, session, tmpl_context as c, url
from pylons.decorators import validate
from pylons.controllers.util import abort, redirect

from prickle.lib.base import BaseController, render

from prickle.model.timesheet import Timesheet, Project, ProjectType, Invoice


log = logging.getLogger(__name__)

class TimesheetController(BaseController):
    def index(self):
        today = datetime.date.today()
        c.title = "Log Time"
        c.entry_title = "Uninvoiced Entries"
        # FIXME: Surely mongoengine knows how to get References by not set?
        c.timesheets = Timesheet.objects(__raw__={'invoice': None}).order_by(
                "-date")
        c.total_time = sum(Decimal(t.duration) for t in c.timesheets)
        c.total_fee = sum(t.fee for t in c.timesheets)
        c.project_list = Project.objects()
        c.date = datetime.date.today()
        c.delete_column = True
        return render('/timesheet/timeform.html')

    @validate(schema=TimesheetForm, form='index')
    def logit(self):
        project, created = Project.objects.get_or_create(
                name=self.form_result['project'])
        if self.form_result['type']:
            type, created = ProjectType.objects.get_or_create(
                    project=project, type=self.form_result['type'])
        else:
            type = None
        timesheet = Timesheet(
                date=datetime.datetime(
                    self.form_result['date'].year,
                    self.form_result['date'].month,
                    self.form_result['date'].day,
                    ),
                duration=self.form_result['duration'],
                project=project,
                type=type,
                description=self.form_result['description'])
        timesheet.save()
        path = request.params.get('next')
        if not path:
            path = url(controller="timesheet", action="index")
        return redirect(path)

    def delete(self, id):
        timesheet = Timesheet.objects.get(id=id)
        timesheet.delete()
        return "deleted"

    def date(self, date):
        c.title = "Log Time for %s" % date
        c.entry_title = "Timesheets for %s" % date
        c.date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        c.timesheets = Timesheet.for_date(c.date)
        c.total_time = sum(t.duration for t in c.timesheets)
        c.total_fee = sum(t.fee for t in c.timesheets)
        c.project_list = Project.objects()
        return render('/timesheet/timeform.html')

    def month(self, year, month):
        month_start = datetime.datetime(int(year), int(month), 1)
        month_end = month_start + relativedelta(months=1) - relativedelta(days=1)
        c.date = month_start.date()
        c.title = "Timesheet summary for %s" % c.date.strftime("%B, %Y")
        c.timesheets = Timesheet.objects(date__gte=month_start,
                date__lte=month_end).order_by("-date")
        c.total_time = sum(t.duration for t in c.timesheets)
        c.total_fee = sum(t.fee for t in c.timesheets)
        c.invoice_column = True
        #FIXME: I'm really tired and suspect this is not the right way to do this
        project_summary = defaultdict(dict) 
        for timesheet in c.timesheets:
            project_summary[timesheet.project.name]['duration'] = \
                    project_summary[timesheet.project.name].setdefault(
                            'duration', 0) + timesheet.duration
            project_summary[timesheet.project.name]['fee'] = \
                    project_summary[timesheet.project.name].setdefault(
                            'fee', 0) + timesheet.fee

        c.project_summary = project_summary
        return render('/timesheet/month_summary.html')
    
    def project(self, id):
        c.project = Project.objects.get(name=id)
        c.timesheets = Timesheet.objects(project=c.project,
                __raw__={'invoice': None}).order_by("-date")
        c.title = "Project Summary for %s" % id
        c.total_time = sum(t.duration for t in c.timesheets)
        c.total_fee = sum(t.fee for t in c.timesheets)
        c.invoices = Invoice.objects(project=c.project)
        c.invoice_totals = {'duration': 0, 'fee': 0, 'total': 0}
        for i in c.invoices:
            c.invoice_totals['duration'] += i.total_duration()
            c.invoice_totals['fee'] += i.total_fee()
            c.invoice_totals['total'] += i.total()
        return render('/timesheet/project_summary.html')

    def types_for_project(self, id):
        project, cr = Project.objects.get_or_create(name=id)
        types = ProjectType.objects(project=project)
        return json.dumps([t.type for t in types])

    def edit(self, id):
        c.timesheet = Timesheet.objects.get(id=id)
        return render('/timesheet/edit_timesheet_form.html')

    @validate(schema=EditTimesheetForm, form='edit')
    def save_edit(self, id):
        c.timesheet = Timesheet.objects.get(id=id)
        c.timesheet.date=datetime.datetime(
                    self.form_result['date'].year,
                    self.form_result['date'].month,
                    self.form_result['date'].day,
                    )
        c.timesheet.duration=self.form_result['duration']
        project, created = Project.objects.get_or_create(
                name=self.form_result['project'])
        if self.form_result['type']:
            type, created = ProjectType.objects.get_or_create(
                    project=project, type=self.form_result['type'])
        else:
            type = None
        c.timesheet.project=project
        c.timesheet.type=type
        c.timesheet.description=self.form_result['description']
        c.timesheet.save()
        c.delete_column = True
        return render('/timesheet/timesheet_row_direct.html')
