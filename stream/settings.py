from pathlib import Path
from decouple import config
import dj_database_url
import os
import logging

BASE_DIR = Path(__file__).resolve().parent.parent

# Add this after your BASE_DIR definition
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# Security
SECRET_KEY = config("SECRET_KEY", default="unsafe-default-secret-key")


# SECURITY WARNING: don't run with debug turned on in production!


DEBUG = False

# Database configuration - comment out local database and set debug to false in production. For local use comment out production database and set debug to true.

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


DATABASES = {"default": dj_database_url.config(default=os.environ.get("DATABASE_URL"))}


ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')


CSRF_TRUSTED_ORIGINS = [
    'https://streamenglish.up.railway.app',
    'https://*.railway.app',
    'https://*.up.railway.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Static and media files
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Update Cloudinary storage settings
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'your_default_cloud_name'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
    'SECURE': True,
    'MEDIA_TAG': 'media',
    'INVALID_VIDEO_ERROR_MESSAGE': 'Please upload a valid video file.',
    'INVALID_IMAGE_ERROR_MESSAGE': 'Please upload a valid image file.',
    'STATIC_TAG': 'static',
}

# Check if all required Cloudinary credentials are available
if all([
    os.environ.get('CLOUDINARY_CLOUD_NAME'),
    os.environ.get('CLOUDINARY_API_KEY'),
    os.environ.get('CLOUDINARY_API_SECRET')
]):
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
    STATICFILES_STORAGE = "cloudinary_storage.storage.StaticHashedCloudinaryStorage"
else:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "whitenoise.runserver_nostatic",
    "cloudinary_storage",
    "cloudinary",
    "django_ckeditor_5",
    "simple_history",
    'widget_tweaks',
    "django.contrib.sitemaps",
    # Internal apps
    "courses",
    "profiles",
    "pages",
    "news",
]

SITE_ID = 1
DJANGO_ADMIN_SITE_URL = 'https://streamenglish.up.railway.app'


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.BrokenLinkEmailsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'profiles.middleware.IPRateLimitMiddleware',
]

ROOT_URLCONF = "stream.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "stream.wsgi.application"


# Security Settings
# SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds

# IP Rate limiting settings
IP_RATE_LIMIT_MAX_ATTEMPTS = 20  # Maximum attempts per IP
IP_RATE_LIMIT_TIMEOUT = 300     # Reset after 5 minutes (in seconds)


# Email settings (for production)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = config('SENDGRID_API_KEY')
SENDGRID_API_KEY = config('SENDGRID_API_KEY', default=None) 
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='streamenglish@outlook.com')
CONTACT_EMAIL='streamenglish@outlook.com'

EMAIL_TIMEOUT = 5  # seconds
EMAIL_MAX_RETRIES = 3

# Account activation settings
ACCOUNT_ACTIVATION_DAYS = 7  # One-week activation window
ACCOUNT_ACTIVATION_LINK_EXPIRED_HOURS = 24 * ACCOUNT_ACTIVATION_DAYS
REGISTRATION_SALT = 'registration'

# Security settings for password reset
PASSWORD_RESET_TIMEOUT = 259200  # 3 days in seconds
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    # Add social providers here if needed
}

# Authentication
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# Login/logout settings
LOGIN_REDIRECT_URL = '/profiles/profile/'
LOGIN_URL = '/profiles/login/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/profiles/login/'


# CKEditor configuration settings 
CKEDITOR_5_UPLOAD_PATH = "uploads/"

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                   'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', 'blockQuote', 'codeBlock', '|',
            'link', 'imageUpload', 'insertTable', 'mediaEmbed', '|',
            'alignment', '|',
            'findAndReplace', '|',
            'undo', 'redo', '|',],
        'height': '300px',
        'width': '100%',
        'removePlugins': ['Title'],
        'contentsCss': [
            '/static/css/dist/styles.css',  # Your Tailwind CSS
        ],
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'font-normal text-gray-600 text-base'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'text-4xl font-extrabold tracking-tight text-gray-900 mb-4'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'text-3xl font-bold text-gray-900 mb-4'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'text-2xl font-semibold text-gray-900 mb-3'},
            ]
        },
    },
}

CKEDITOR_5_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'