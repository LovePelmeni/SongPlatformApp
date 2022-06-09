from __future__ import annotations

import unittest, pytest
from django import test
from parameterized import parameterized
try:
    from VideoHost.main import models
except(ImportError,):
    import models

@pytest.fixture(scope='module')
def client():
    yield test.Client(enforce_csrf_checks=True)
from .tests import BaseRequestEndpointTestCase

class TestSubscriptionCase(BaseRequestEndpointTestCase):

    def setUp(self):
        self.data = {'username': 'some-username',
        'password': 'some-password', 'phone_number': 'some-phone_number'}

    def run(self, result: unittest.result.TestResult | None = ...) -> unittest.result.TestResult | None:
        self.run_tests()
        return super().run(result)