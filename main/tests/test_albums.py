import pytest
import parameterized
try:
    from VideoHost.main import models
except(ImportError,):
    import models


class TestAlbumCase(TestCase):

    def setUp(self):
        self.data = {'username': 'some-username', 'password': 'some-password',
        'phone_number': 'some-phone_number'}

    @parameterized.expand([])
    def test_create_album(self):
        pass

    @parameterized.expand([])
    def test_delete_album(self):
        pass

    @parameterized.expand([])
    def test_update_album(self):
        pass
