"""
Django settings for delta project.

Generated by 'django-admin startproject' using Django 2.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
#from kombu.entity import Exchange, Queue

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import sys
from celery.schedules import crontab
from decouple import config
import urllib
from kombu.entity import Exchange, Queue

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'clf+_mut(l6()+oqc004^#1i_s5r15(*kdi_mridaaehdv!rk%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition



ROOT_URLCONF = 'delta.urls'

TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates')

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_PATH],
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

WSGI_APPLICATION = 'delta.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'eventstore': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

DELTA_MESH_DB = {
    "HOST": "127.0.0.1",
    "PORT": "8123",
    "USERNAME": "admin",
    "PASSWORD": "admin"
}




# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

ENV = "local"



CELERY_BROKER_URL = 'sqs://{0}:{1}@'.format(
    urllib.parse.quote(AWS_ACCESS_KEY, safe=''),
    urllib.parse.quote(AWS_SECRET_KEY, safe='')
)

CELERY_BROKER_TRANSPORT_OPTIONS = {
    'region': os.environ.get("DELTA_SQS_REGION"),
    'polling_interval': 3,
    'visibility_timeout': 3600,
    'https_validate_certificates': False,
}

CELERY_BROKER_TRANSPORT_OPTIONS['queue_name_prefix'] = 'LOCAL-DELTA-'

# CELERY_TASK_SERIALIZER = 'pickle'
# CELERY_RESULT_SERIALIZER = 'pickle'
# CELERY_ACCEPT_CONTENT = {'pickle'}


#CELERY_SEND_TASK_ERROR_EMAILS = True

CELERY_DEFAULT_QUEUE = 'MAIN'

CELERY_RESULT_BACKEND = "django-db"

CELERY_IMPORTS = ["profiles.tasks", "metric.services", "metric.intergrations", "metric.tasks"]


CELERY_QUEUES = (
    Queue('MAIN', Exchange('default'), routing_key='default'),
)

# CELERY_ROUTES = {
#     'notifier.tasks.handle_event': {
#         'queue': 'NOTIFICATION-TASK',
#     },
#     'event_logger_client.tasks.handle_log': {
#         'queue': 'EVENT-LOG-TASK',
#     },
#     'graphs.tasks.update_graphs_overview': {
#         'queue': 'PROLONGED-TASK',
#     },
#     'reports.tasks.update_reports_overview': {
#         'queue': 'PROLONGED-TASK',
#     },
# }

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'LocalMem1',
    }
}

GEOIP_PATH = os.path.join(BASE_DIR, 'geodata')
GEOIP_CITY = os.path.join(BASE_DIR, 'geodata/GeoLite2-City.mmdb')


REDIS_QUEUE = 'redis://localhost:6379/0'

REDIS_URL = os.environ.get("DELTA_REDIS_URL","redis://127.0.0.1:6379/0")


DATADOG_TRACE = {"DEFAULT_SERVICE": "DELTA", "TAGS": {"env": "staging"}, "ENABLED": False}


SNS_TOPIC = "arn:aws:sns:ap-south-1:614358145679:DELTA-MISC"

AWS_DEFAULT_ENV = os.environ.get('AWS_ENV', 'ap-south-1')



CELERY_BEAT_SCHEDULE = {
    #'sync_and_process_aum_data': {'task': 'metric.tasks.sync_and_process_aum_data', 'schedule': crontab(hour=9, minute=30)}, #everday 3 pm
    'partial_sync_and_process_overview_of_users': {
        'task': 'metric.tasks.partial_sync_and_process_overview_of_users',
        'schedule': crontab(minute="*/15")
    },
    # 'partial_sync_and_process_partner_metric': {
    #     'task': 'metric.tasks.partial_sync_and_process_partner_metric',
    #     'schedule': crontab(minute="*/19")
    # },
    'sync_trak_overview': {
        'task': 'profiles.tasks.sync_trak_overview_task', 'schedule': crontab(hour="*", minute=0)
    },
    # Every 15 mins between 7:30 to 22:30 IST
    'sync_user_profile_from_hagrid': {
        'task': 'profiles.tasks.sync_user_profile_from_hagrid', 'schedule': crontab(hour="2-17", minute="*/15")
    },
}

CELERY_RESULT_EXPIRES = 4*60




INDIAN_TZ = 'Asia/Kolkata'

# MONITORING
OTEL_EXPORTER_OTLP_ENDPOINT="http://otel-agent-service.monitoring:4317"
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="http://otel-agent-service.monitoring:4317"
OTEL_METRIC_EXPORT_INTERVAL=3000    # OTEL data flush interval in millisecond
APP_MONITORING="on"   # ('on', 'yes', 'true', '1') are considered as switch-on
MONITOR_CELERY=1    # only "1" is considered as switch-on
ENABLE_MONITORING = os.environ.get('ENABLE_MONITORING', False)