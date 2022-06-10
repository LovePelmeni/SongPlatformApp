from __future__ import annotations

import tempfile
import typing, pydantic

import boto3, botocore.exceptions
from celery import shared_task

from django.conf import settings
import logging, datetime
from . import exceptions

logger = logging.getLogger(__name__)
import dropbox.exceptions



dropbox_app = dropbox.Dropbox(oauth2_access_token=getattr(settings, 'DROPBOX_ACCESS_TOKEN'))

AUDIO_FILES_TEMP_PATH = tempfile.mktemp(prefix='/song/audio/')
PREVIEW_FILES_TEMP_PATH = tempfile.mktemp(prefix='/song/preview/')
AVATAR_FILES_TEMP_PATH = tempfile.mktemp(prefix='/avatar/')


from abc import ABC
class DropBoxFile(object):

    """
    / * Class Represents Dropbox file.
    """
    def __init__(self, file, content_type: typing.Literal["media/png",
    "media/jpeg", "media/jpg", "audio/mp3", "audio/mp4", "audio/wav"] | str):
        try:
            self.file = file
            self.extension = '.%s' + content_type.split('/')[1]
            self.name = file.name if hasattr(file, 'name')\
            else 'file-%s' % (datetime.datetime.now()) + self.extension
        except() as exception:
            logger.error('Exception has been raised while DropBox File creation. %s' % exception)
            raise NotImplementedError


class DropBoxBucket(object):
    """
    / * Class Represents DropBox Bucket and supports following operations.
    / * It is already supposed that all the path names already exist...
    """
    def __init__(self, path):
        self.path = path

    def get(self, file_link):
        try:
            directories = getattr(settings, 'TEMP_FILES_DIR')
            file = dropbox_app.files_download_to_file(path=file_link, download_path=directories)
            return file
        except(dropbox.files.DownloadError,):
            raise exceptions.DropboxBucketDoesNotExist()

    def upload(self, file, content_type) -> DropBoxFileLink:
        try:
            file = DropBoxFile(file=file, content_type=content_type)
            path = self.path + file.name
            with open(file.file, mode='rb') as upload_file:
                dropbox_app.files_upload(f=upload_file.read(), path=path)
            return path

        except(exceptions.DropboxBucketDoesNotExist, AttributeError,):
            logger.error('DROPBOX BUCKET NOT FOUND. name = %s' % self.path)
            raise exceptions.DropboxFileUploadFailed


    def update(self, file_link: str, new_file) -> DropBoxFileLink | Exception:
        try:
            if not self.remove(file_link=file_link):
                raise NotImplementedError
            new_file_link = self.upload(file=new_file)
            return new_file_link
        except(NotImplementedError):
            raise exceptions.DropboxFileUploadFailed


    def remove(self, file_link: str):
        try:
            dropbox_app.files_delete_v2(path=file_link)
        except(dropbox.exceptions.DropboxException, ):
            raise exceptions.DropboxFileRemoveFailed





