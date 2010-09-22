from decimal import Decimal
import datetime
import couchdb
from couchdb.mapping import Document, DateField, TextField, DecimalField, ViewField
from couchdb.design import ViewDefinition


couch = couchdb.Server()

TIMESHEET_DB = "prickle_timesheets"

try:
    timesheets = couch[TIMESHEET_DB]
except couchdb.http.ResourceNotFound:
    timesheets = couch.create(TIMESHEET_DB)

class Timesheet(Document):
    date = DateField()
    duration = DecimalField()
    project = TextField()
    description = TextField()
    _all_timesheets = ViewField('timesheets', '''\
            function(doc) {
                emit(doc.name, doc);
            }''')
    _by_date = ViewField('by_date', '''\
            function(doc) {
                emit(doc.date, doc);
            }''')
    _by_project = ViewField('by_project', '''\
            function(doc) {
                emit(doc.project, doc);
            }''')

    @classmethod
    def all_timesheets(cls):
        return cls._all_timesheets(timesheets)

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
    def for_project(cls, project):
        return cls._by_project(timesheets, key=project)

    @classmethod
    def project_list(cls):
        return projects(timesheets, group=True)

    def store(self, db=timesheets):
        # default database
        super(Timesheet, self).store(db)

projects = ViewDefinition("projects", "all", '''\
    function(doc) {
        if (doc.project) {
            emit(doc.project, 1);
        }
    }''',
    '''\
    function(keys, values, rereduce) {
        return sum(values);
    }''')

projects.sync(timesheets)
Timesheet._all_timesheets.sync(timesheets)
Timesheet._by_date.sync(timesheets)
Timesheet._by_project.sync(timesheets)
