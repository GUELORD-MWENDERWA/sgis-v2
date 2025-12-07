from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

# SQLite pour dev
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS en dev (frontend local)
CORS_ALLOW_ALL_ORIGINS = True
