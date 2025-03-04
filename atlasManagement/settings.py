"""
Django settings for atlasManagement project.

Generated by 'django-admin startproject' using Django 4.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from pathlib import Path
from django.contrib.messages import constants as messages

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#&8)1d8!!o+no6_y4x$*m0+yzxmk=1rb$jidq5bfemljmm7h6w'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
APPEND_SLASH = False

ALLOWED_HOSTS = ['654a-190-114-39-196.ngrok-free.app','127.0.0.1', 'localhost']

CSRF_TRUSTED_ORIGINS = [
    'https://654a-190-114-39-196.ngrok-free.app'
]

LANGUAGE_CODE = 'es'

# Application definition

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}




INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app.apps.AppConfig',
    'colorfield',
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'django.contrib.humanize',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'atlasManagement.middleware.CurrentUserMiddleware',
    'atlasManagement.middleware.UserActivityLoggerMiddleware',
]

ROOT_URLCONF = 'atlasManagement.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.views.user_permissions',
            ],
        },
    },
]

WSGI_APPLICATION = 'atlasManagement.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bbdd_atlas_gestion',
        'USER': 'ghotless',
        'PASSWORD': 'M0nst3r',
        'HOST': '64.23.159.80',
        'PORT': '5433',
    },
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

ATLAS_PRINT_AGENT_TOKEN = "Bearer 1234abcd"

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "app" / "static",
]


CRISPY_TEMPLATE_PACK = 'bootstrap5'
# Bootstrap v5.3.3

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

# Configuración del backend de correos
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Configuración SMTP basada en Ferozo
EMAIL_HOST = 'c2661241.ferozo.com' 
EMAIL_PORT = 465 
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True  
EMAIL_HOST_USER = 'contacto@atlasgestion.cl' 
EMAIL_HOST_PASSWORD = 'Mnx@6vJ3iZ' 

# Configuración adicional opcional
DEFAULT_FROM_EMAIL = 'contacto@atlasgestion.cl'

LOGIN_REDIRECT_URL = 'home' 

LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')