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
from decimal import Decimal


from pylons.decorators import validate
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from prickle.lib.base import BaseController, render

from prickle.model.timesheet import Timesheet, Project, ProjectType
from prickle.forms.timesheet import RateForm

log = logging.getLogger(__name__)

class ProjectsController(BaseController):

    def list(self):
        c.projects = Project.project_list()
        return render('/project/project_list.html')

    def view(self, id):
        project = Project.load_or_create(id)
        c.project = project
        return render('/project/project_form.html')

    @validate(schema=RateForm, form='view')
    def edit(self, id):
        project = Project.load_or_create(id)
        project.rate = self.form_result['rate']
        project.store()
        return redirect(url(controller="timesheet", action="index"))

    @validate(schema=RateForm, form='view')
    def type_rate(self, project, type):
        project_type = ProjectType.load_or_create(project, type)
        project_type.rate = self.form_result['rate']
        project_type.store()
        return redirect(url(controller="timesheet", action="project",
            id=project))
