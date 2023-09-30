from firebase_admin import credentials
import firebase_admin
import os
import environ

env = environ.Env()
environ.Env.read_env()

if env('ENV_KEY') == 'production':
    from .production import *
elif env('ENV_KEY') == 'staging':
    from .staging import *
elif env('ENV_KEY') == 'local':
    from .local import *

# put firebase_key.json in to environment variable
cred = credentials.Certificate(os.path.join(
    BASE_DIR, 'settings/firebase_key.json'))
default_app = firebase_admin.initialize_app(cred)
