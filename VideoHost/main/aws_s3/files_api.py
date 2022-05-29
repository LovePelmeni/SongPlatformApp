from __future__ import annotations
import boto3, botocore.exceptions
from celery import shared_task

from django.conf import settings
import logging, datetime

logger = logging.getLogger(__name__)

class AwsFileNotFoundError(BaseException):

    def __init__(self, status_code, message=None):
        self.message = message
        self.status_code = status_code

    def __call__(self):
        raise self


def _get_file_aws_file(bucket_name, file_link: str):
    """This method gets video from aws platform using file id...."""
    try:
        s3 = boto3.resource('s3')
        if not bucket_name in s3.buckets.all():
            raise botocore.exceptions.ConfigNotFound()

        file = s3.Bucket(bucket_name).download_file(
        key=settings.AWS_SECRET_ACCESS_KEY, destfile=file_link)
        return file

    except botocore.exceptions.ClientError as aws_ex:
        if aws_ex.response['Error']['Code'] == '404':
            message = 'Video file is not found :('
            raise AwsFileNotFoundError(
            message=message, status_code=404)


def _save_file_to_aws(file, bucket_name):
    """This method saves video to aws platform...."""
    import os
    file_unique_name = os.path.splitext(file.name)[0] + '-%s' % datetime.datetime.now() + request.user.id
    boto3.resource('s3').Bucket(bucket_name).upload_file(
    filename=file_unique_name, filetype=file.content_type)
    logger.debug('file has been uploaded... %s, time: %s' % (file.name, datetime.datetime.now()))
    return file_unique_name


def _delete_from_aws_storage(bucket_name: str, filelink: str):
    try:
        boto3.resource('s3').Bucket(bucket_name).remove_file(filename=filelink)
        return True
    except():
        return False


def update_file_in_aws(request, file_url, bucket_name, updated_file):
    if not _delete_from_aws_storage(bucket_name=bucket_name, filelink=file_url):
        logger.error('could not update image.')
        raise NotImplementedError()
    else:
        file_link = _save_file_to_aws(bucket_name=bucket_name, file=updated_file)
        return file_link
