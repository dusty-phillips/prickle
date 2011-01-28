# This is a very dirty, hackish script to port a previous
# couchdb based prickle to mongodb. It worked for me...

from decimal import Decimal
import datetime
import couchdb
from couchdb.mapping import Document, DateField, TextField, DecimalField, ViewField
from couchdb.design import ViewDefinition
import sys
import mongoengine

# pass the name of the couchdb prefix on the command line
# it'll be either prickle_ or will have been set in the production.ini
# file
prefix = sys.argv[1]
from prickle.model import timesheet as mongo_models
# pass the name of the mongodb prefix as the second one. prickle is the
# default, or it is set in production.ini
mongoengine.connect(sys.argv[2])

# Clean out the existing mongodb collection. Not necessarily a good thing


couch = couchdb.Server()

TIMESHEET_DB = prefix + "timesheets"
PROJECT_DB = prefix + "projects"
TYPE_DB = prefix + "project_types"
INVOICE_DB = prefix + "invoices"

try:
    timesheets = couch[TIMESHEET_DB]
except couchdb.http.ResourceNotFound:
    timesheets = couch.create(TIMESHEET_DB)

try:
    projects = couch[PROJECT_DB]
except couchdb.http.ResourceNotFound:
    projects = couch.create(PROJECT_DB)

try:
    project_types = couch[TYPE_DB]
except couchdb.http.ResourceNotFound:
    project_types = couch.create(TYPE_DB)

try:
    invoices = couch[INVOICE_DB]
except couchdb.http.ResourceNotFound:
    invoices = couch.create(INVOICE_DB)


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

class Invoice(Document):
    date = DateField()
    bill_to = TextField()
    project = TextField()
    rate = DecimalField()
    tax = DecimalField(default=0.0)

    _all_invoices = ViewField('invoices', '''\
            function(doc) {
                if (doc._id != "no invoice") {
                    emit(doc.date, doc);
                }
            }''')
    _by_project = ViewField('by_project', '''\
            function(doc) {
                if (doc._id != "no invoice") {
                    emit(doc.project, doc);
                }
            }''')

    def store(self, db=invoices):
        # default database
        super(Invoice, self).store(db)

    @classmethod
    def all_invoices(cls):
        return cls._all_invoices(invoices, descending=True)

    @classmethod
    def for_project(cls, project):
        return cls._by_project(invoices, key=project)

    @classmethod
    def load(cls, id, db=invoices):
        return super(Invoice, cls).load(db, id)

    @classmethod
    def next_invoice_number(cls):
        result = last_invoice_num(invoices)
        if result.rows:
            return result.rows[0]['value'] + 1
        return 1

last_invoice_num = ViewDefinition("last_num", "all", '''\
    function(doc) {
        emit(1, parseInt(doc._id));
    }''',
    '''\
    function(keys, values, rereduce) {
        var max = 0;
        for (var i in values) {
            if (values[i] > max) {
                max = values[i];
            }
        }
        return max;
    }''')

project_names.sync(timesheets)
type_names.sync(timesheets)
Timesheet._all_timesheets.sync(timesheets)
Timesheet._by_date.sync(timesheets)
Timesheet._by_invoice.sync(timesheets)
Timesheet._by_project.sync(timesheets)
Timesheet._by_project_unbilled.sync(timesheets)
Timesheet._by_date_unbilled.sync(timesheets)
ProjectType._by_project_type.sync(project_types)

last_invoice_num.sync(invoices)
Invoice._all_invoices.sync(invoices)
Invoice._by_project.sync(invoices)

project_names = Project.project_list()
for name in project_names:
    print("migrating project %s" % name)
    project = Project.load(name)
    mongo_project, cr = mongo_models.Project.objects.get_or_create(name=name)
    if project:
        mongo_project.rate = project.rate
        mongo_project.save()
    type_name_list = ProjectType.type_list(name)
    for type_name in type_name_list:
        print("migrating project type %s %s" % (name, type))
        if type_name:
            type = ProjectType.load_or_create(name, type_name)
            
            mongo_type, cr = mongo_models.ProjectType.objects.get_or_create(
                    project=mongo_project,
                    type=type_name)
            mongo_type.rate = type.rate
            mongo_type.save()


for invoice in Invoice.all_invoices():
    print("migrating invoice %s" % (invoice.id)) 
    mongo_invoice, cr = mongo_models.Invoice.objects.get_or_create(
            number=int(invoice.id))
    mongo_invoice.date = datetime.datetime(
            invoice.date.year, invoice.date.month, invoice.date.day)
    mongo_invoice.bill_to = invoice.bill_to
    mongo_invoice.project = mongo_models.Project.objects.get(
            name=invoice.project)
    mongo_invoice.rate = invoice.rate
    mongo_invoice.tax = invoice.tax
    mongo_invoice.save()

unbilled_invoice = mongo_models.Invoice(number=-1)
unbilled_invoice.save()

# All the previous migrations are idempotent, this one will create new
# timesheets each time
for timesheet in Timesheet.all_timesheets():
    print("migrating timesheet %s" % timesheet)
    mongo_timesheet = mongo_models.Timesheet(
            date = datetime.datetime(
                timesheet.date.year, timesheet.date.month, timesheet.date.day),
            duration = timesheet.duration,
            project = mongo_models.Project.objects.get(
                name=timesheet.project),
            description = timesheet.description,
            archived_rate=timesheet.archived_rate)
    if timesheet.type:
        mongo_timesheet.type, cr = mongo_models.ProjectType.objects.get_or_create(
                project__name=timesheet.project, type=timesheet.type)
    if timesheet.invoice:
        try:
            mongo_timesheet.invoice, cr = mongo_models.Invoice.objects.get_or_create(
                    number=int(timesheet.invoice))
        except ValueError: # unbilled or no invoice
            mongo_timesheet.invoice = unbilled_invoice
    mongo_timesheet.save()

print("Migration complete")
