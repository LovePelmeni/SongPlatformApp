from __future__ import annotations

import typing, pydantic

import boto3, botocore.exceptions
from celery import shared_task

from django.conf import settings
import logging, datetime
from . import exceptions

logger = logging.getLogger(__name__)

import dropbox.exceptions
dropbox_app = dropbox.Dropbox(app_key=getattr(settings, 'DROPBOX_ACCESS_KEY'),
app_secret=getattr(settings, 'DROPBOX_ACCESS_SECRET'))


class DropBoxFileLink(pydantic.BaseModel):

    file_link: str

    @pydantic.validator('file_link')
    def validate_file_link(cls, value):
        if not re.match(pattern='link-pattern', string=value):
            raise pydantic.ValidationError()
        return value


class DropBoxBucket(object):
    """
    / * Class Represents AWS S3 Bucket and supports following operations.
    / * It is already supposed that all the paths and buckets already exist...
    """
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def get_bucket_path(self) -> str:
        try:
            return getattr(settings, 'BUCKET_PATHS')[self.bucket_name]
        except(KeyError,):
            raise exceptions.DropboxBucketDoesNotExist()

    def upload(self, file, filename: typing.Optional[str]) -> DropBoxFileLink:
        try:
            path = self.get_bucket_path()
            extension = os.path.splitext(file)[1]
            if not filename:
                filename = os.path.splitext(file)[0]
            path += '/%s.%s' % (filename, extension)
            with open(file, mode='rb') as upload_file:
                dropbox_app.files_upload(f=upload_file.read(), path=path)
            return DropBoxFileLink(file_link=path)
        except(exceptions.DropboxBucketDoesNotExist,):
            logger.error('DROPBOX BUCKER NOT FOUND. name = %s' % self.bucket_name)

    def update(self, file_link: str, new_file, filename: typing.Optional[str]) -> DropBoxFileLink:
        try:
            if not self.remove(file_link=file_link):
                raise NotImplementedError
            new_file_link = self.upload(file=new_file, filename=filename)
            return new_file_link
        except(NotImplementedError):
            raise NotImplementedError

    def remove(self, file_link: str) -> None | Exception:
        try:
            dropbox_app.files_delete_v2(path=file_link)
        except(dropbox.exceptions.DropboxException, ):
            raise NotImplementedError
