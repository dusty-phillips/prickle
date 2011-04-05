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

    @classmethod
    def for_date(cls, date):
        start = datetime.datetime(date.year, date.month, date.day)
        end = datetime.datetime(date.year, date.month, date.day, 23, 59, 59)
        return Timesheet.objects(date__gte=start, date__lte=end)

class Project(mongoengine.Document):
    name = mongoengine.StringField(primary_key=True)
    rate = mongoengine.DecimalField(default=0)

    def __str__(self):
        return self.name

    def project_types(self):
        return ProjectType.objects(project=self)

class ProjectType(mongoengine.Document):
    project = mongoengine.ReferenceField(Project)
    type = mongoengine.StringField()
    rate = mongoengine.DecimalField(default=0)

    def __str__(self):
        return self.type

class Invoice(mongoengine.Document):
    number = mongoengine.IntField(unique=True)
    date = mongoengine.DateTimeField()
    bill_to = mongoengine.StringField()
    project = mongoengine.ReferenceField(Project)
    rate = mongoengine.DecimalField()
    tax = mongoengine.DecimalField(default=0.0)

    @classmethod
    def next_invoice_number(cls):
        invoices = cls.objects.order_by("number")
        count = invoices.count()
        if count:
            return invoices[count-1].number + 1
        return 1

    def __str__(self):
        return str(self.number)

    def total_duration(self):
        timesheets = Timesheet.objects(invoice=self)
        return sum(t.duration for t in timesheets)

    def total_fee(self):
        timesheets = Timesheet.objects(invoice=self)
        return sum(t.fee for t in timesheets)

    def total(self):
        total = self.total_fee()
        return total + total * self.tax * Decimal('.01')
