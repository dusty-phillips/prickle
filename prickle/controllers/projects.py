import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from prickle.lib.base import BaseController, render

from prickle.model.timesheet import Timesheet

log = logging.getLogger(__name__)

class ProjectsController(BaseController):

    def list(self):
        c.projects = Timesheet.project_list()
        return render('/project_list.html')

    def view(self, id):
        return "project view " + id
