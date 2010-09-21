from decimal import Decimal
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

    @classmethod
    def all_timesheets(cls):
        return cls._all_timesheets(timesheets)

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
