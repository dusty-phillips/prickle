import logging
import datetime

from decimal import Decimal

from formencode import validators
import formencode


from pylons import request, response, session, tmpl_context as c, url
from pylons.decorators import validate
from pylons.controllers.util import abort, redirect

from prickle.lib.base import BaseController, render

from prickle.model.timesheet import Timesheet


log = logging.getLogger(__name__)


# Really, where should this class go?
class DurationValidator(validators.FancyValidator):
    '''Validates input is in HH:MM format, and converts it to (or from) a
    decimal recording the number of hours.'''
    def _to_python(self, value, state):
        try:
            hours, colon, minutes = value.partition(":")
            hours = int(hours)
            minutes = int(minutes)
            if minutes > 60 or minutes < 0:
                raise validators.Invalid("Duration minutes should be in [0,60]")
        except ValueError:
            raise validators.Invalid("Duration format should be HH:MM")
        else:
            fraction = Decimal(minutes) / 60
            return hours + fraction

    def _from_python(self, value, state):
        hours = int(d)
        minutes = int(d * 60 % 60)
        return "%#02d:%#02d" % (hours, minutes)

class DateValidator(validators.FancyValidator):
    format = "%Y-%m-%d"
    def _to_python(self, value, state):
        return datetime.datetime.strptime(value, self.format).date()

    def _from_python(self, value, state):
        return value.strftime(self.format)

# This one, too?
class TimesheetForm(formencode.Schema):
    date = DateValidator()
    duration = DurationValidator()
    project = formencode.validators.String(not_empty=True)
    description = formencode.validators.String(not_empty=True)

class TimesheetController(BaseController):
    def index(self):
        c.existing_timesheets = Timesheet.all_timesheets()
        c.project_list = [l.key for l in Timesheet.project_list()]
        c.date = datetime.date.today()
        return render('/timeform.html')

    @validate(schema=TimesheetForm, form='index')
    def logit(self):
        timesheet = Timesheet(
                date=self.form_result['date'],
                duration=self.form_result['duration'],
                project=self.form_result['project'],
                description=self.form_result['description'])
        timesheet.store()
        return redirect(url(controller="timesheet", action="index"))
