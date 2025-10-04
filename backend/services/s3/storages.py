from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class PublicMediaStorage(S3Boto3Storage):
    location = "media/public"
    file_overwrite = False
    custom_domain = getattr(settings, "AWS_S3_CUSTOM_DOMAIN", None)


class PrivateMediaStorage(S3Boto3Storage):
    location = "media/private"
    default_acl = "private"
    file_overwrite = False
    custom_domain = getattr(settings, "AWS_S3_CUSTOM_DOMAIN", None)


class TestingPublicMediaStorage(S3Boto3Storage):
    location = "test/media/public"
    file_overwrite = False
    custom_domain = getattr(settings, "AWS_S3_CUSTOM_DOMAIN", None)


class TestingPrivateMediaStorage(S3Boto3Storage):
    location = "test/media/private"
    default_acl = "private"
    file_overwrite = False
    custom_domain = getattr(settings, "AWS_S3_CUSTOM_DOMAIN", None)
