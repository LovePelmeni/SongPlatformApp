from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class StaticStorage(S3Boto3Storage):

    location = settings.AWS_STATIC_LOCATION


class PublicStorage(S3Boto3Storage):

    location = settings.AWS_PUBLIC_MEDIA_LOCATION
    file_overwrite = False


class PrivateStorage(S3Boto3Storage):

    location = settings.AWS_PRIVATE_MEDIA_LOCATION
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False


