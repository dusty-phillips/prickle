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
        c.projects = Project.objects()
        return render('/project/project_list.html')

    def view(self, id):
        c.project, created = Project.objects.get_or_create(name=id)
        return render('/project/project_form.html')

    @validate(schema=RateForm, form='view')
    def edit(self, id):
        project, created = Project.objects.get_or_create(name=id)
        project.rate = self.form_result['rate']
        project.save()
        return redirect(url(controller="timesheet", action="index"))

    @validate(schema=RateForm, form='view')
    def type_rate(self, project, type):
        project, created = Project.objects.get_or_create(name=project)
        project_type, created = ProjectType.objects.get_or_create(
                project=project, type=type)
        project_type.rate = self.form_result['rate']
        project_type.save()
        return redirect(url(controller="timesheet", action="project",
            id=project))
