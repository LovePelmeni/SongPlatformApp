from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from VideoHost.main import models
from VideoHost.main.groups import generate_etag
import requests

class TestGroupCase(TestCase):

    def setUp(self):

        self.file_url = ''
        self.edit_data = {'group_name': 'Another-Group-Name'}

        self.group = models.ChatGroup.objects.create('http://localhost:8000/create/chat/group/',
        data={'group_name': 'Chat-Group', 'avatar': SimpleUploadedFile(content=open(self.file_url),
        content_type='media/png', name=open(self.file_url).name)})

    def test_edit_group(self):

        if not hasattr(self.group, 'etag'):
            self.group.etag = generate_etag(self.group)
            self.group.save()

        response = self.client.Session()
        response.headers.update({'Last-Modified': self.group.last_updated, 'If-Match': self.group.etag})

        response.get('http://localhost:8000/get/group/', data={
        'group_name': self.group.group_name})

        if response.status_code == 304:
            edit_response = self.client.post('http://localhost:8000/edit/chat/group/',
            data=self.edit_data)
            self.assertIn(edit_response.status_code, container=[412, 200], msg='EDIT TEST FAILED!')
        self.assertIn(response.status_code, container=[200, 304], msg='EDIT TEST FAILED, INVALID RESPONSE CODE!')





