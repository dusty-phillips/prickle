"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password
from pylons import url
import datetime
import dateutil.relativedelta

def nl2br(value):
    return value.replace("\n", "<br />")

def previous_month(date):
    return date-dateutil.relativedelta.relativedelta(months=1)

def next_month(date):
    return date+dateutil.relativedelta.relativedelta(months=1)
