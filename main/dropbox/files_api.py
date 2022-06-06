from __future__ import annotations

import typing

import boto3, botocore.exceptions
from celery import shared_task

from django.conf import settings
import logging, datetime
from . import exceptions

logger = logging.getLogger(__name__)

import dropbox.exceptions
dropbox_app = dropbox.Dropbox(app_key=getattr(settings, 'DROPBOX_ACCESS_KEY'))


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
    """
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def get_bucket_path(self) -> str:
        pass

    def upload(self, file, filename: typing.Optional[str]) -> DropBoxFileLink:

        path = self.get_bucket_path()
        extension = os.path.splitext(file)[1]
        if not filename:
            filename = os.path.splitext(file)[0]
        path += '/%s.%s' % (filename, extension)
        with open(file, mode='rb') as upload_file:
            dropbox_app.files_upload(f=upload_file.read(), path=path)
        return DropBoxFileLink(file_link=path)

    def update(self, file_link: str, new_file, filename: typing.Optional[str]) -> DropBoxFileLink:
        pass

    def remove(self, file_link: str) -> bool:
        pass