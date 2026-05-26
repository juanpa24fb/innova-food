"""
Django settings for config project.
Proyecto: Innova Food
Configurado para desarrollo local, Render y Cloudinary.
"""

from pathlib import Path
import os
import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent


# Seguridad
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-0hd9o0!6-$tj=j_#hljk!7yrgh#c2^f#!kxx(cv2ochuv5a5%h'
)

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    '.onrender.com,localhost,127.0.0.1'
).split(',')


# Activar Cloudinary solo cuando la variable USE_CLOUDINARY=True
USE_CLOUDINARY = os.environ.get('USE_CLOUDINARY', 'False') == 'True'


# Aplicaciones instaladas
INSTALLED_APPS = [
    'tienda',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    # Cloudinary para guardar imágenes y comprobantes en la nube
    'cloudinary_storage',
    'cloudinary',

    'django.contrib.staticfiles',
]


# Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # WhiteNoise permite servir archivos CSS, JS e imágenes estáticas en Render
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'config.urls'


# Templates HTML
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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


WSGI_APPLICATION = 'config.wsgi.application'


# Base de datos
# Localmente usa SQLite.
# En Render usará PostgreSQL si existe DATABASE_URL.
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}


# Validación de contraseñas
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


# Idioma y zona horaria
LANGUAGE_CODE = 'es-ec'

TIME_ZONE = 'America/Guayaquil'

USE_I18N = True

USE_TZ = True


# Archivos estáticos: CSS, JS, imágenes del diseño
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'tienda' / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'


# Archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Almacenamiento
# Localmente guarda imágenes en /media.
# En Render, si USE_CLOUDINARY=True, guarda imágenes y comprobantes en Cloudinary.
if USE_CLOUDINARY:
    STORAGES = {
        'default': {
            'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }
else:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }


# Redirecciones de login/logout
LOGIN_URL = 'login'

LOGIN_REDIRECT_URL = 'inicio'

LOGOUT_REDIRECT_URL = 'inicio'


# Seguridad extra para Render
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Campo automático por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
