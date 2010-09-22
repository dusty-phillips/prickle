import logging
from decimal import Decimal
import formencode
from formencode import validators

from pylons.decorators import validate
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from prickle.lib.base import BaseController, render

from prickle.model.timesheet import Timesheet, Project

log = logging.getLogger(__name__)

class DecimalValidator(validators.FancyValidator):
    def _to_python(self, value, state):
        return Decimal(value)

    def _from_python(self, value, state):
        return str(value)

class ProjectForm(formencode.Schema):
    rate = DecimalValidator()

class ProjectsController(BaseController):

    def list(self):
        c.projects = Project.project_list()
        return render('/project_list.html')

    def view(self, id):
        project = Project.load_or_create(id)
        c.project = project
        return render('/project_form.html')

    @validate(schema=ProjectForm, form='view')
    def edit(self, id):
        project = Project.load_or_create(id)
        project.rate = self.form_result['rate']
        project.store()
        return redirect(url(controller="timesheet", action="index"))
