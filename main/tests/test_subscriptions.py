import unittest, pytest
from django import test



class TestSubscriptionCase(test.TestCase):

    def setUp(self):
        self.data = {'username': 'some-username', 'password': 'some-password',
                     'phone_number': 'some-phone_number'}

    def test_create_subscription(self):
        pass

    def test_delete_subscription(self):
        pass

    def test_update_subscription(self):
        pass
