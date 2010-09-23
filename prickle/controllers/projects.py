import logging
from decimal import Decimal


from pylons.decorators import validate
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from prickle.lib.base import BaseController, render

from prickle.model.timesheet import Timesheet, Project
from prickle.forms.timesheet import ProjectForm

log = logging.getLogger(__name__)

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
