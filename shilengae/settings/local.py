from .base import *

DEBUG = False
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

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
