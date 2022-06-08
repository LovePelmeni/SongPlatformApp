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


class TestSubscriptionCase(test.TestCase):

    def setUp(self):
        self.data = {'username': 'some-username',
        'password': 'some-password', 'phone_number': 'some-phone_number'}

    @paramitrized.expand([{'username': 'some-username', 'password': 'some-password',
    'phone_number': 'some-phone_number'}, client])
    def test_create_subscription(self, subscription_data, client):
        pass

    @paramitrized.expand([1, client])
    def test_delete_subscription(self, subscription_id, client):
        pass

    @paramitrized.expand([{'username': 'some-username', 'password': 'some-password',
    'phone_number': 'some-phone_number'}, 1, client])
    def test_update_subscription(self, subscription_data, subscription_id, client):
        pass


