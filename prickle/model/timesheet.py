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

from decimal import Decimal
import datetime
import mongoengine
from pylons import config

db_name = config.get('database_name', 'prickle')

mongoengine.connect(db_name)

class Timesheet(mongoengine.Document):
    date = mongoengine.DateTimeField()
    duration = mongoengine.DecimalField()
    project = mongoengine.ReferenceField('Project')
    type = mongoengine.ReferenceField('ProjectType')
    description = mongoengine.StringField()
    invoice = mongoengine.ReferenceField('Invoice')
    archived_rate = mongoengine.DecimalField()

    #FIXME: These properties have not been defined
    @property
    def rate(self):
        if self.archived_rate:
            return self.archived_rate
        if self.invoice and self.invoice.rate:
            return self.invoice.rate
        if self.type and self.type.rate:
            return self.type.rate
        if self.project and self.project.rate:
            return self.project.rate
        return 0 

    @property
    def fee(self):
        return self.rate * self.duration

class Project(mongoengine.Document):
    name = mongoengine.StringField(primary_key=True)
    rate = mongoengine.DecimalField(default=0)

    def __str__(self):
        return self.name

class ProjectType(mongoengine.Document):
    project = mongoengine.ReferenceField(Project)
    type = mongoengine.StringField()
    rate = mongoengine.DecimalField(default=0)

# There is an invoice.py models file but maybe it doesn't need
# to exist...
class Invoice(mongoengine.Document):
    date = mongoengine.DateTimeField()
    bill_to = mongoengine.StringField()
    project = mongoengine.ReferenceField(Project)
    rate = mongoengine.DecimalField()
    tax = mongoengine.DecimalField(default=0.0)

# FIXME REMOVE
# Below here, find legacy couchdb code for reference
if False:
    class Timesheet(Document):
        date = DateField()
        duration = DecimalField()
        project = TextField()
        type = TextField(default='')
        description = TextField()
        invoice = TextField(default='')
        archived_rate = DecimalField()
        _all_timesheets = ViewField('timesheets', '''\
                function(doc) {
                    emit(doc.project, doc);
                }''')
        _by_date = ViewField('by_date', '''\
                function(doc) {
                    emit(doc.date, doc);
                }''')
        _by_project = ViewField('by_project', '''\
                function(doc) {
                    emit(doc.project, doc);
                }''')
        _by_date_unbilled = ViewField('by_date', '''\
                function(doc) {
                    if (!doc.invoice) {
                        emit(doc.date, doc);
                    }
                }''')
        _by_project_unbilled = ViewField('by_project', '''\
                function(doc) {
                    if (!doc.invoice) {
                        emit(doc.project, doc);
                    }
                }''')
        _by_invoice = ViewField('by_invoice', '''\
                function(doc) {
                    if(doc.invoice) {
                        emit(doc.invoice, doc);
                    }
                }''')

        @classmethod
        def load(cls, id, db=timesheets):
            return super(Timesheet, cls).load(db, id)

        @classmethod
        def all_timesheets(cls, unbilled=False):
            if not unbilled:
                return cls._all_timesheets(timesheets)
            else:
                return cls._by_date_unbilled(timesheets, descending=True)

        @classmethod
        def for_date(cls, date):
            if isinstance(date, datetime.date):
                date = datetime.date.strftime("%Y-m-%d")
            return cls._by_date(timesheets, key=date)

        @classmethod
        def for_month(cls, year, month):
            month = int(month)
            return cls._by_date(timesheets, startkey="%s-%#02d-01" % (year, month),
                    endkey="%s-%#02d-00"% (year, month+1))

        @classmethod
        def for_project(cls, project, unbilled=False):
            if not unbilled:
                projects = cls._by_project(timesheets, key=project)
            else:
                projects = cls._by_project_unbilled(timesheets, key=project)

            return sorted(projects, key=lambda s: s.date, reverse=True)

        @classmethod
        def for_invoice(cls, invoice):
            return sorted(cls._by_invoice(timesheets, key=invoice),
                    key=lambda s: s.date, reverse=True)

        def store(self, db=timesheets):
            # default database
            super(Timesheet, self).store(db)

        @property
        def rate(self):
            project = Project.load(self.project)
            if self.archived_rate:
                return self.archived_rate
            if self.invoice:
                invoice = Invoice.load(self.invoice)
                if invoice and invoice.rate:
                    return invoice.rate
            if self.type:
                type = ProjectType.load_or_create(self.project, self.type)
                if type and type.rate:
                    return type.rate
            if project:
                return project.rate
            return 0 

        @property
        def fee(self):
            return self.rate * self.duration

    class Project(Document):
        rate = DecimalField(default=0)

        def store(self, db=projects):
            # default database
            super(Project, self).store(db)

        @property
        def project_types(self):
            return [ProjectType.load_or_create(self.id, t
                ) for t in ProjectType.type_list(self.id)]

        @classmethod
        def project_list(cls):
            # Note that this is getting project names from the timesheet
            # database. This allows users to create projects that don't exist
            # yet
            return [p.key for p in project_names(timesheets, group=True)]

        @classmethod
        def load(cls, id, db=projects):
            return super(Project, cls).load(db, id)

        @classmethod
        def load_or_create(cls, id, db=projects):
            project = cls.load(id, db)
            if not project:
                project = cls(id)
            return project

    class ProjectType(Document):
        project = TextField()
        type = TextField()
        rate = DecimalField(default=0)

        _by_project_type = ViewField('by_project_type', '''\
                function(doc) {
                        emit([doc.project, doc.type], doc);
                }''')

        @classmethod
        def type_list(cls, project):
            '''List all the types associated with timesheets for a given project'''
            return [t.key[1] for t in type_names(timesheets, group=True, 
                startkey=[project], endkey=[project, {}], inclusive_end=True)]

        def store(self, db=project_types):
            # default database
            super(ProjectType, self).store(db)

        @classmethod
        def load_or_create(cls, project, type):
            project_type = cls._by_project_type(project_types, key=[project, type])
            if project_type:
                return project_type.rows[0]
            return cls(project=project, type=type)

    project_names = ViewDefinition("projects", "all", '''\
        function(doc) {
            if (doc.project) {
                emit(doc.project, 1);
            }
        }''',
        '''\
        function(keys, values, rereduce) {
            return sum(values);
        }''')
    type_names = ViewDefinition("types", "by_project", '''\
        function(doc) {
            if (doc.project) {
                emit([doc.project, doc.type || ''], 1);
            }
        }''',
        '''function(keys, values, rereduce) {
                return sum(values);
        }''')
