from .base import *

DEBUG = True

# Credentials for superuser created via `manage.py create_dev_superuser`
DEV_SUPERUSER_EMAIL = 'admin@admin.com'
DEV_SUPERUSER_PASSWORD = 'admin123'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.environ['POSTGRES_HOST'],
        'PORT': os.environ['POSTGRES_PORT'],
        'ATOMIC_REQUESTS': True
    }
}



# Mail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Uncomment and set settings below
# EMAIL_HOST =
# EMAIL_PORT =
# EMAIL_HOST_USER =
# EMAIL_HOST_PASSWORD =

DEFAULT_FROM_EMAIL = 'vdrive_postmaster@atomcream.com'

SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URL = 'http://127.0.0.1:8000/social/complete/google-oauth2/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'http://127.0.0.1:8000/social/complete/google-oauth2/'