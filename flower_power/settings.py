import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ON_RENDER = os.environ.get('RENDER', '').lower() == 'true'
DEBUG = os.environ.get('DJANGO_DEBUG', '0' if ON_RENDER else '1') == '1'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if not DEBUG:
        raise RuntimeError('Set DJANGO_SECRET_KEY for production')
    secret_file = BASE_DIR / '.local-secret'
    if not secret_file.exists():
        secret_file.write_text(secrets.token_urlsafe(50), encoding='utf-8')
    SECRET_KEY = secret_file.read_text(encoding='utf-8')
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,[::1]').split(',')
RENDER_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_HOSTNAME)
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]
if RENDER_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_HOSTNAME}')
INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'shop',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware', 'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
ROOT_URLCONF = 'flower_power.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True, 'OPTIONS': {'context_processors': [
        'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages', 'shop.context_processors.cart_summary',
    ]},
}]
WSGI_APPLICATION = 'flower_power.wsgi.application'
DATABASES = {'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': Path(os.environ.get('DJANGO_DB_PATH', str(BASE_DIR / 'db.sqlite3'))),
    'OPTIONS': {'timeout': 20},
}}
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Kaliningrad'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = Path(os.environ.get('DJANGO_MEDIA_ROOT', str(BASE_DIR / 'media')))
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage' if DEBUG else 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    if ON_RENDER:
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
        SECURE_REDIRECT_EXEMPT = [r'^healthz/$']
