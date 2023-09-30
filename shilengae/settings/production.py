import environ
from .base import *

env = environ.Env()
environ.Env.read_env()

DEBUG = False
DATABASES = {
    'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME'),
            'USER': env('RDS_USERNAME'),
            'PASSWORD': env('RDS_PASSWORD'),
            'HOST': env('DB_HOST'),
            'PORT': env('DB_PORT'),
    },
}
