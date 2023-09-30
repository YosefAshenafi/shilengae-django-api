from .base import *

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'shilengae',
        'USER': 'shilengae_dev_user',
        'PASSWORD': 'dev_password',
        'HOST': '0.0.0.0',
        'PORT': '5432'
    },
}


