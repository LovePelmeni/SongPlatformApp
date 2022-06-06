from django.test import TestCase, override_settings



class TestUserModel(TestCase):

    def setUp(self):
        self.data = {'username': 'some-username', 'password': 'some-password',
        'phone_number': 'some-phone_number'}

    def test_create_user(self):
        pass

    def test_delete_user(self):
        pass

    def test_update_user(self):
        pass


class TestSongModel(TestCase):

    def setUp(self):
        self.data = {'username': 'some-username', 'password': 'some-password',
                     'phone_number': 'some-phone_number'}

    def test_create_user(self):
        pass

    def test_delete_user(self):
        pass

    def test_update_user(self):
        pass


class TestSubscriptionModel(TestCase):

    def setUp(self):
        self.data = {'username': 'some-username', 'password': 'some-password',
                     'phone_number': 'some-phone_number'}

    def test_create_user(self):
        pass

    def test_delete_user(self):
        pass

    def test_update_user(self):
        pass


class TestAlbumModel(TestCase):

    def setUp(self):
        self.data = {'username': 'some-username', 'password': 'some-password',
                     'phone_number': 'some-phone_number'}

    def test_create_user(self):
        pass

    def test_delete_user(self):
        pass

    def test_update_user(self):
        pass



