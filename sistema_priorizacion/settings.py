from pathlib import Path

import os

from dotenv import load_dotenv

load_dotenv()


# ======================================================
# BASE
# ======================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ======================================================
# SEGURIDAD
# ======================================================

SECRET_KEY = 'django-insecure-dev-key'

DEBUG = True

ALLOWED_HOSTS = ['*']


# ======================================================
# APPS
# ======================================================

INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'dashboard',
    'cargas',
    'facturas',
    'api'
]


# ======================================================
# MIDDLEWARE
# ======================================================

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ======================================================
# URLS
# ======================================================

ROOT_URLCONF = 'sistema_priorizacion.urls'


# ======================================================
# TEMPLATES
# ======================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            BASE_DIR / 'templates'
        ],

        'APP_DIRS': True,

        'OPTIONS': {

            'context_processors': [

                'django.template.context_processors.request',

                'django.contrib.auth.context_processors.auth',

                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ======================================================
# WSGI
# ======================================================

WSGI_APPLICATION = 'sistema_priorizacion.wsgi.application'


# ======================================================
# DATABASE
# ======================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',

        'NAME': 'neondb',

        'USER': 'neondb_owner',

        'PASSWORD': os.getenv('DB_PASSWORD'),

        'HOST': 'ep-young-field-a8zqsjf8-pooler.eastus2.azure.neon.tech',

        'PORT': '5432',

        'OPTIONS': {
            'sslmode': 'require'
        }
    }
}


# ======================================================
# PASSWORD VALIDATION
# ======================================================

AUTH_PASSWORD_VALIDATORS = []


# ======================================================
# LANGUAGE
# ======================================================

LANGUAGE_CODE = 'es-mx'

TIME_ZONE = 'America/Mexico_City'

USE_I18N = True

USE_TZ = True


# ======================================================
# STATIC
# ======================================================

STATIC_URL = 'static/'


# ======================================================
# MEDIA
# ======================================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# ======================================================
# DEFAULT PK
# ======================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'