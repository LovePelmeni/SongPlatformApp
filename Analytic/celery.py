from __future__ import absolute_import

import crontab
from celery import Celery
import os
from django.conf import settings
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Analytic.settings')
celery_app = Celery('Analytic', broker=settings.BROKER_URL)

celery_app.conf.update(
    result_backend=settings.CELERY_RESULT_BACKEND,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    enable_utc=True,
    timezone=settings.CELERY_TIMEZONE,
    result_expires=None,
    broker=settings.BROKER_URL
)

celery_app.config_from_object(settings)
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
