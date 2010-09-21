from prickle.tests import *

class TestTimesheetController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='timesheet', action='index'))
        # Test response...
