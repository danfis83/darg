# -*- coding: utf-8 -*-
"""
Django settings for darg project.

Generated by 'django-admin startproject' using Django 1.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from kombu import Exchange, Queue

VERSION = '0.3.53'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

SITE_ID = 1

ALLOWED_HOSTS = [
    'www.das-aktienregister.ch',
    'app.das-aktienregister.ch',
    'www.dasaktienregister.ch',
    'dasaktienregister.ch',
    'das-aktienregister.ch',
    ]

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.humanize',
    'django.contrib.flatpages',

    'registration',
    'rest_framework',
    'rest_framework.authtoken',
    'raven.contrib.django.raven_compat',
    'sorl.thumbnail',
    'djrill',
    'djcelery',
    'django_markdown',
    'markdownx',
    'reversion',

    # -- zinnia
    'django_comments',
    'mptt',
    'tagging',
    'zinnia_bootstrap',
    'zinnia',
    # --

    'shareholder',
    'services',
    'company',
    'project',
    'utils',
)

MIDDLEWARE_CLASSES = (
    'reversion.middleware.RevisionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        # 'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'project.context_processors.tracking',
                'zinnia.context_processors.version',
            ],
            'loaders': (
                'django.template.loaders.filesystem.Loader',
                'app_namespace.Loader',
                'django.template.loaders.app_directories.Loader',
            ),
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': ''
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'de'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# -- LOGGING

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'handlers': ['console', 'sentry'],
        'level': 'WARNING',
        'formatter': 'verbose',
    },
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d '
                      '%(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.'
                     'SentryHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
        },
        'celery': {
            'level': 'WARNING',
            'handlers': ['sentry', 'console'],
            'propagate': False,
        },
        'selenium': {
            'level': 'WARNING',
            'handlers': ['console'],
            'propagate': False,
        },
        'easyprocess': {
            'level': 'WARNING',
            'handlers': ['console'],
            'propagate': False,
        },
        'shareholder': {
            'level': 'INFO',
            'handlers': ['console'],
        },
    },
}

# -- CACHE
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

# -- EMAIL
ADMINS = ()
SERVER_EMAIL = 'no-reply@das-aktienregister.ch'
EMAIL_SUBJECT_PREFIX = '[darg] '

MANAGERS = ADMINS + ()

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# -- STATIC FILES
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    # os.path.join(BASE_DIR, 'static', 'minified'),
    os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'media', 'static')

MEDIA_ROOT = 'media'  # used also by zinnia for path inside static. is relative

MEDIA_URL = '/media/'

# --- REGISTRATION
REGISTRATION_OPEN = True        # If True, users can register
ACCOUNT_ACTIVATION_DAYS = 7     # One-week activation window; you may, of cour
REGISTRATION_AUTO_LOGIN = True  # If True, the user will be automatically logg
LOGIN_REDIRECT_URL = '/start/'  # The page you want users to arrive at after t
LOGIN_URL = '/accounts/login/'  # The page users are directed to if they are n

# --- REST
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'PAGE_SIZE': 1000,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}
# angular does want this
APPEND_SLASH = False

# --- I18N
# add here for app module dirs to show up under 'project' filter in rosetta
LOCALE_PATHS = (
    './i18n/locale/',
    './shareholder/locale/',
    './services/locale/',
)

# --- Sentry
RAVEN_CONFIG = {
    'dsn': '',
}

# -- TEST RUNNEr
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# -- TRACKING
TRACKING_ENABLED = not DEBUG
TRACKING_CODE = ""

# -- BLOG
ZINNIA_UPLOAD_TO = os.path.join(MEDIA_ROOT, 'blog')
ZINNIA_MARKUP_LANGUAGE = 'markdown'

# -- SENDFILE for downloads
SENDFILE_BACKEND = 'sendfile.backends.nginx'
SENDFILE_ROOT = os.path.join(MEDIA_ROOT, 'private')
SENDFILE_URL = "/media/private"

MANDRILL_API_KEY = "<your Mandrill key>"
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
DEFAULT_FROM_EMAIL = "info@das-aktienregister.ch"
MANDRILL_SETTINGS = {
    'tracking_domain': 'mail.das-aktienregister.ch',
    'track_opens': True,
}

# --- CELERY
# CELERY_ALWAYS_EAGER = False # use default anyway
CELERYD_HIJACK_ROOT_LOGGER = False
CELERY_DEFAULT_QUEUE = 'darg'
CELERY_QUEUES = (
    Queue('darg', Exchange('darg'), routing_key='darg'),
)
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
BROKER_URL = 'amqp://darg:darg@localhost:5672/darg'

# --- MARKDOWN X

MARKDOWNX_MARKDOWNIFY_FUNCTION = 'markdownx.utils.markdownify'
MARKDOWNX_MARKDOWN_EXTENSIONS = [
    'markdown.extensions.extra',
    'markdown.extensions.nl2br',
    'markdown.extensions.smarty',
]

# Media path
MARKDOWNX_MEDIA_PATH = 'f/'  # Path, where images will be stored in MEDIA_ROOT folder

try:
    from project.settings.local import *
except ImportError:
    print "no local conf"
