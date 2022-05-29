from __future__ import absolute_import
from celery import Celery
import os
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VideoHost.settings')
celery_app = Celery('VideoHost', broker=settings.BROKER_URL)

celery_app.conf.update(
    result_backend=settings.CELERY_RESULT_BACKEND,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    enable_utc=True,
    timezone=settings.CELERY_TIMEZONE,
)

celery_app.config_from_object('django.conf:settings')
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
