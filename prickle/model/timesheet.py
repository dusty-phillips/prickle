from decimal import Decimal
import couchdb
from couchdb.mapping import Document, TextField, DecimalField


couch = couchdb.Server()

TIMESHEET_DB = "prickle_timesheets"

try:
    timesheets = couch[TIMESHEET_DB]
except couchdb.http.ResourceNotFound:
    timesheets = couch.create(TIMESHEET_DB)

class Timesheet(Document):
    duration = DecimalField()
    project = TextField()
    description = TextField()

    def store(self, db=TIMESHEET_DB):
        # default database
        super(Timesheet, self).store(db)
