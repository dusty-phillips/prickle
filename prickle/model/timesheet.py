from decimal import Decimal
import datetime
import couchdb
from couchdb.mapping import Document, DateField, TextField, DecimalField, ViewField
from couchdb.design import ViewDefinition
from prickle.model.invoice import Invoice
from pylons import config

prefix = config.get('couchdb_prefix', 'prickle_')

couch = couchdb.Server()

TIMESHEET_DB = prefix + "timesheets"
PROJECT_DB = prefix + "projects"

try:
    timesheets = couch[TIMESHEET_DB]
except couchdb.http.ResourceNotFound:
    timesheets = couch.create(TIMESHEET_DB)

try:
    projects = couch[PROJECT_DB]
except couchdb.http.ResourceNotFound:
    projects = couch.create(PROJECT_DB)

class Timesheet(Document):
    date = DateField()
    duration = DecimalField()
    project = TextField()
    description = TextField()
    invoice = TextField(default='')
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
            return cls._by_project(timesheets, key=project)
        else:
            return cls._by_project_unbilled(timesheets, key=project)

    @classmethod
    def for_invoice(cls, invoice):
        return cls._by_invoice(timesheets, key=invoice)

    def store(self, db=timesheets):
        # default database
        super(Timesheet, self).store(db)

    @property
    def rate(self):
        project = Project.load(self.project)
        if self.invoice:
            invoice = Invoice.load(self.invoice)
            if invoice:
                return invoice.rate
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

project_names.sync(timesheets)
Timesheet._all_timesheets.sync(timesheets)
Timesheet._by_date.sync(timesheets)
Timesheet._by_invoice.sync(timesheets)
Timesheet._by_project.sync(timesheets)
Timesheet._by_project_unbilled.sync(timesheets)
Timesheet._by_date_unbilled.sync(timesheets)
