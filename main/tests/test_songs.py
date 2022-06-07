import dropbox, unittest
import pytest
from django import test
import signal

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
class TestSongsCase(unittest.TestCase):

    def setUp(self):
        self.client = client
        self.preview = bytes()
        self.audio_file = bytes()
        self.user = models.CustomUser.objects.create(username='TestUser',
        email='TestEmail', password='TestPassword')
        self.song = models.Song.objects.create(audio_file=self.audio_file, preview=self.preview, owner=self.user)
        self.client = client

    def test_song_create(self, dropbox_app):
        import requests
        self.client.force_login(self.user, backend=getattr(settings, 'AUTHENTICATION_BACKENDS')[0])
        response = self.client.post('http://localhost:8000/song/',
        timeout=10, headers={'CSRF-Token'})
        self.assertIn(response.status_code, [200, 201])

    def test_update(self, dropbox_app):
        import requests
        response = self.client.put('http://localhost:8000/song/?song_id=%s' % self.song.id,
        timeout=10, headers={'Content-Type': 'application/json'})
        self.assertEquals(response.status_code, (200, 201))

    def test_song_delete(self, dropbox_app):
        import requests
        response = self.client.delete('http://localhost:8000/song/?song_id=%s' % self.song.id,
        timeout=10, headers={'Content-Type': 'application/json'})
        self.assertEquals(response.status_code, (200, 201))
        self.assertLess(len(models.Song.objects.all()), 2)


