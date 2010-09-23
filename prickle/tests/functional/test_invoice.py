from prickle.tests import *

class TestInvoiceController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='invoice', action='index'))
        # Test response...
