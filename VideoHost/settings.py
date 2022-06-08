"""
Django settings for VideoHost project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
import redis

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-cl71#vtl!s58j$65*6u%o#krsltkl^k8*2ycq73478c5yqid!b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',

    'django.contrib.contenttypes',
    'django.contrib.sessions',

    'django.contrib.messages',
    'django.contrib.staticfiles',

    'main',
    'rest_framework',
    'corsheaders',
    'drf_yasg',
]


AUTHENTICATION_BACKENDS = (

    'main.backends.AdminAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)


MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'main.middlewares.SetUpAuthorizationHeaderMiddleware',
    'main.middlewares.CheckBlockedUserMiddleware'

]

ROOT_URLCONF = 'VideoHost.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTH_USER_MODEL = 'main.CustomUser'
WSGI_APPLICATION = 'VideoHost.wsgi.application'

REST_FRAMEWORK = {

    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),

    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),

    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    )
}

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG'
        },
        'file_handler': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'file_log.log'
        }
    },
    'loggers': {
        'main': {
            'handlers': ['console', 'file_handler'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

if not DEBUG:

    import os
    DATABASES = {

        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_NAME'),
            'USER': os.environ.get('POSTGRES_USER'),

            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': os.environ.get('POSTGRES_HOST'),
            'PORT': os.environ.get('POSTGRES_PORT')
        },
    }

    SONG_APP_DOMAIN = os.environ.get('SONG_APP_DOMAIN')
    FRONTEND_APPLICATION_DOMAIN = os.environ.get('VUE_APP_DOMAIN')
    SUBSCRIPTION_APP_DOMAIN = os.environ.get('SUBSCRIPTION_APP_DOMAIN')

    CORS_ALLOWED_ORIGINS = [

        'http://%s:8000' % SONG_APP_DOMAIN,
        'http://%s:3000' % FRONTEND_APPLICATION_DOMAIN,
        'http://%s:8033' % SUBSCRIPTION_APP_DOMAIN

    ]

    CACHE = {
        'default': {
            'BACKEND': 'django.core.cache.backends.RedisCache',
            'LOCATION': 'http://%s:6379' % os.environ.get('REDIS_HOST'),
            'OPTIONS': {
                'PASSWORD': os.environ.get('REDIS_PASSWORD')
            }
        }
    }

    DROPBOX_SONG_PREVIEW_FILE_PATH = os.environ.get('DROPBOX_SONG_PREVIEW_FILE_PATH')
    DROPBOX_SONG_AUDIO_FILE_PATH = os.environ.get('DROPBOX_SONG_AUDIO_FILE_PATH')
    DROPBOX_SUBSCRIPTION_PREVIEW_FILE_PATH = os.environ.get('DROPBOX_SUBSCRIPTION_PREVIEW_FILE_PATH')
    DROPBOX_CUSTOMER_AVATAR_FILE_PATH = os.environ.get('DROPBOX_CUSTOMER_AVATAR_FILE_PATH')

    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
    RABBITMQ_USER = os.getenv('RABBITMQ_USER')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')
    RABBITMQ_PORT = os.getenv('RABBITMQ_PORT')
    RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST')

    DROPBOX_ACCESS_KEY = os.environ.get('DROPBOX_ACCESS_KEY')

else:

    DATABASES = {

        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'web_app_db',
            'USER': 'postgres',

            'PASSWORD': 'Kirill',
            'HOST': 'localhost',
            'PORT': 5434
        },
    }

    CORS_ALLOW_ALL_ORIGINS = True

    CHANNEL_LAYER = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [('127.0.0.1', 6379)],
            },
        }}

    CACHE = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

    import os
    DROPBOX_SONG_PREVIEW_FILE_PATH = os.environ.get('DROPBOX_SONG_PREVIEW_FILE_PATH')
    DROPBOX_SONG_AUDIO_FILE_PATH = os.environ.get('DROPBOX_SONG_AUDIO_FILE_PATH')
    DROPBOX_SUBSCRIPTION_PREVIEW_FILE_PATH = os.environ.get('DROPBOX_SUBSCRIPTION_PREVIEW_FILE_PATH')
    DROPBOX_CUSTOMER_AVATAR_FILE_PATH = os.environ.get('DROPBOX_CUSTOMER_AVATAR_FILE_PATH')

    RABBITMQ_HOST = 'localhost'
    RABBITMQ_USER = 'rabbitmq_user'
    RABBITMQ_PASSWORD = 'rabbitmq_password'
    RABBITMQ_PORT = '5671'
    RABBITMQ_VHOST = 'rabbitmq_vhost'

    DROPBOX_ACCESS_KEY = 'bep2nuhf1wmtq3y'
    DROPBOX_ACCESS_SECRET = 't2nfz143f8iqdc9'


SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = 'images/'

import os

STATIC_ROOT = os.path.join(BASE_DIR, 'main/static/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'main/static/images/')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

