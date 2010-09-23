import datetime
from decimal import Decimal
from formencode import validators
import formencode

#These validators may be useful elsewhere
class DurationValidator(validators.FancyValidator):
    '''Validates input is in HH:MM format, and converts it to (or from) a
    decimal recording the number of hours.'''
    def _to_python(self, value, state):
        try:
            hours, colon, minutes = value.partition(":")
            hours = int(hours)
            minutes = int(minutes)
            if minutes > 60 or minutes < 0:
                raise validators.Invalid("Duration minutes should be in [0,60]", value, state)
        except ValueError:
            raise validators.Invalid("Duration format should be HH:MM", value, state)
        else:
            fraction = Decimal(minutes) / 60
            return hours + fraction

    def _from_python(self, value, state):
        hours = int(d)
        minutes = int(d * 60 % 60)
        return "%#02d:%#02d" % (hours, minutes)

class DateValidator(validators.FancyValidator):
    format = "%Y-%m-%d"
    def _to_python(self, value, state):
        try:
            return datetime.datetime.strptime(value, self.format).date()
        except ValueError as e:
            raise validators.Invalid("%s does not match format %s" % (
                value, self.format), value, state)

    def _from_python(self, value, state):
        return value.strftime(self.format)

class DecimalValidator(validators.FancyValidator):
    def _to_python(self, value, state):
        return Decimal(value)

    def _from_python(self, value, state):
        return str(value)
