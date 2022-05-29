from django.test import TestCase, override_settings



class TestUserModel(TestCase):

    def setUp(self):
        self.data = {'username': 'some-username', 'password': 'some-password',
        'phone_number': 'some-phone_number'}

    @override_settings(LOGIN_URL='login/user/')
    def test_create_user(self):
        response = self.client.post('http://127.0.0.1:8000/create/user/', data=self.data)
        self.assertRedirects(response, 'login/user/')

