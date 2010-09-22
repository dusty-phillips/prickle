from prickle.tests import *

class TestProjectsController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='projects', action='index'))
        # Test response...
