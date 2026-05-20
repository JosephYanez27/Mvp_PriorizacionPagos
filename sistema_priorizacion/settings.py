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

DEBUG = False

if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.onrender.com']


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

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',

#         'NAME': 'neondb',

#         'USER': 'neondb_owner',

#         'PASSWORD': os.getenv('DB_PASSWORD'),

#         'HOST': 'ep-young-field-a8zqsjf8-pooler.eastus2.azure.neon.tech',

#         'PORT': '5432',

#         'OPTIONS': {
#             'sslmode': 'require'
#         }
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'neondb',                                                 # Extraído de /neondb
        'USER': 'neondb_owner',                                           # Extraído antes del :
        'PASSWORD': os.getenv('DB_PASSWORD', 'npg_2muH4oKkvpEa'),                                 # Tu contraseña real temporal
        'HOST': 'ep-young-field-a8zqsjf8-pooler.eastus2.azure.neon.tech', # El servidor de Neon
        'PORT': '5432',                                                   # Puerto estándar de Postgres
        'OPTIONS': {
            'sslmode': 'require',                                         # Equivalente a ?sslmode=require
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

from pathlib import Path

# Asegúrate de que BASE_DIR esté definido arriba en tu archivo
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = 'static/'

# Añade esta configuración para indicarle a Django la ruta de la carpeta static raíz
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
# ======================================================
# MEDIA
# ======================================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# ======================================================
# DEFAULT PK
# ======================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'