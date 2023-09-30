from .base import *

DEBUG = False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'shilengae_staging',
        'USER': 'shilengae_dev_user',
        'PASSWORD': 'dev_password',
        'HOST': '0.0.0.0',
        'PORT': '5432'
    },
}
