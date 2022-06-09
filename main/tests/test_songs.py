import django.core.files.images
import pytest, signal, dropbox, unittest

from django import test
try:
    from VideoHost.main import models
except(ImportError,):
    import models

from parameterized import parameterized


@pytest.fixture(scope='module')
def dropbox_app():
    yield dropbox.Dropbox(
    app_secret=getattr(settings, 'DROPBOX_APP_SECRET'))

@pytest.fixture(scope='module')
def client():
    yield test.client.Client(enforce_csrf_checks=True)


DROPBOX_TEST_APP_KEY = '' # replace it with your test dropbox app key
DROPBOX_TEST_APP_SECRET = '' # replace it with your test dropbox app secret


@override_settings(DROPBOX_APP_KEY=DROPBOX_TEST_APP_KEY, DROPBOX_APP_SECRET=DROPBOX_TEST_APP_SECRET)
class TestSongsCase(test.TransactionTestCase):

    def setUp(self):

        self.audio_bytes_content = bytes()
        self.preview = django.core.files.images.ImageFile(file='png', name='test_preview')
        self.audio_file = django.core.files.base.ContentFile(content=self.audio_bytes_content)
        self.user = models.CustomUser.objects.create(username='TestUser',
        email='TestEmail', password='TestPassword')
        self.song = models.Song.objects.create(audio_file=self.audio_file, preview=self.preview, owner=self.user)
        pytest.paraself.test_song_update()

    @staticmethod
    def dropbox_TearDown(dropbox_app: dropbox.Dropbox) -> bool:
        import requests, dropbox.exceptions
        response = requests.get('http://api.dropboxapi.com/2/files/list_folder/',
        headers={'Authorization': "Basic %s %s" % (DROPBOX_TEST_APP_KEY, DROPBOX_TEST_APP_SECRET)})
        response.raise_for_status()
        try:
            if not len(json.loads(response.text).get('files')):
                return True
            for file in json.loads(response.text)['files']:
                dropbox_app.files_delete_v2(path=file['path'])
            return True
        except(dropbox.exceptions.DropboxException):
            raise NotImplementedError

    def tearDown(self) -> None:
        """
        / * Clear Dropbox bucket if some sort of data has been found. After Tests.
        """
        try:
            return super().tearDown()
        except():
            raise NotImplementedError

    @parameterized.expand([{'username': 'some-username', 'password': 'some-password',
    'phone_number': 'some-phone_number'}, client])
    def test_song_create(self, song_data, client):
        import requests
        client.force_login(self.user, backend=getattr(settings, 'AUTHENTICATION_BACKENDS')[0])
        response = client.post('http://localhost:8000/song/',
        timeout=10, headers={'CSRF-Token'}, data=song_data)
        self.assertIn(response.status_code, [200, 201])
        self.assertGreater(len(models.Song.objects.all()), 1)


    @paramitrized.expand([{'username': 'some-username', 'password': 'some-password',
    'phone_number': 'some-phone_number'}, 1, client])
    def test_song_update(self, song_data, song_id,  client):
        import requests
        response = client.put('http://localhost:8000/song/?song_id=%s' % song_id,
        timeout=10, data=song_data, headers={'Content-Type': 'application/json'})
        self.assertEquals(response.status_code, (200, 201))


    @paramitrized.expand([1, client])
    def test_song_delete(self, song_id, client):
        import requests
        response = client.delete('http://localhost:8000/song/?song_id=%s' % song_id,
        timeout=10, headers={'Content-Type': 'application/json'})
        self.assertEquals(response.status_code, (200, 201))
        self.assertLess(len(models.Song.objects.all()), 2)


class TestTopWeekSongsCase(test.TransactionTestCase):

    def setUp(self) -> None:
        self.song_id = models.Song.objects.create(song_name='Some Song',
        some_description='Some Description')

    def test_get_top_week_song(self, client):
        response = client.get('http://localhost:8000/get/week/song/',
        params={'song_id': self.song_id}, timeout=10)
        self.assertEquals(response.status_code, 200)
        self.assertIn('song', json.loads(response.read().decode('utf-8')).keys())

    def test_get_top_week_songs(self, client):
        response = client.get('http://localhost:8000/get/week/songs/')
        self.assertEquals(response.status_code, 200)
        self.assertIn('', json.loads(response.read().decode('utf-8')).keys())



