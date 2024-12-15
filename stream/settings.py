from pathlib import Path
from decouple import config
import environ
import os
import logging

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env()

# Add this after your BASE_DIR definition

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}

# Security
SECRET_KEY = config("SECRET_KEY", default="unsafe-default-secret-key")


# SECURITY WARNING: don't run with debug turned on in production!


DEBUG = False

# Database configuration - comment out local database and set debug to false in production. For local use comment out production database and set debug to true.

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "mysql.connector.django",
        "NAME": env("DATABASE_NAME"),
        "USER": env("DATABASE_USER"),
        "PASSWORD": env("DATABASE_PASSWORD"),
        "HOST": env("DATABASE_HOST", default="localhost"),
        "PORT": env("DATABASE_PORT", default="3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "use_unicode": True,
        },
    }
}

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

CSRF_TRUSTED_ORIGINS = [
    "https://streamenglish-co-uk.stackstaging.com",
    "https://streamenglish.co.uk",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

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
    "django_ckeditor_5",
    "widget_tweaks",
    "django.contrib.sitemaps",
    # Internal apps
    "courses",
    "profiles",
    "pages",
    "news",
    "shop",
]

SITE_ID = 1

# Site URLs
if DEBUG:
    SITE_URL = "http://127.0.0.1:8000"  # Development URL
else:
    SITE_URL = "https://streamenglish-co-uk.stackstaging.com"  # Production URL

# Update admin site URL
DJANGO_ADMIN_SITE_URL = "https://streamenglish-co-uk.stackstaging.com"


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
    "profiles.middleware.IPRateLimitMiddleware",
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
                "shop.context_processors.cart",
            ],
        },
    },
]

WSGI_APPLICATION = "stream.wsgi.application"

# Update media and static settings
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Ensure these directories exist
MEDIA_SECURE = os.path.join(MEDIA_ROOT, "secure_downloads")
MEDIA_PUBLIC = os.path.join(MEDIA_ROOT, "public")

# Static files configuration
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# Add secure storage settings
SECURE_DOWNLOADS_URL = (
    "/downloads/"  # This will be handled by a view, not direct access
)

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"


# Security Settings
# SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds

# IP Rate limiting settings
IP_RATE_LIMIT_MAX_ATTEMPTS = 20  # Maximum attempts per IP
IP_RATE_LIMIT_TIMEOUT = 300  # Reset after 5 minutes (in seconds)


# Email settings (for production)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = config("SENDGRID_API_KEY")
SENDGRID_API_KEY = config("SENDGRID_API_KEY", default=None)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="streamenglish@outlook.com")
CONTACT_EMAIL = "streamenglish@outlook.com"


EMAIL_TIMEOUT = 5  # seconds
EMAIL_MAX_RETRIES = 3

# Account activation settings
ACCOUNT_ACTIVATION_DAYS = 7  # One-week activation window
ACCOUNT_ACTIVATION_LINK_EXPIRED_HOURS = 24 * ACCOUNT_ACTIVATION_DAYS
REGISTRATION_SALT = "registration"

# Security settings for password reset
PASSWORD_RESET_TIMEOUT = 259200  # 3 days in seconds
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    # Add social providers here if needed
}

# Authentication
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# Login/logout settings
LOGIN_REDIRECT_URL = "/profiles/profile/"
LOGIN_URL = "/profiles/login/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/profiles/login/"


# CKEditor configuration settings
CKEDITOR_5_UPLOAD_PATH = "uploads/"

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "imageUpload",
            "blockQuote",
            "codeBlock",
            "|",
            "link",
            "imageUpload",
            "insertTable",
            "mediaEmbed",
            "|",
            "alignment",
            "|",
            "findAndReplace",
            "|",
            "undo",
            "redo",
            "|",
        ],
        "height": "300px",
        "width": "100%",
        "removePlugins": ["Title"],
        "contentsCss": [
            "/static/css/dist/styles.css",  # Your Tailwind CSS
        ],
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "font-normal text-gray-600 text-base",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "text-4xl font-extrabold tracking-tight text-gray-900 mb-4",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "text-3xl font-bold text-gray-900 mb-4",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "text-2xl font-semibold text-gray-900 mb-3",
                },
            ]
        },
    },
}

CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"


# Stripe Settings
STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLIC_KEY", default="")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET", default="")
STRIPE_CURRENCY = "gbp"

# Shop Email
SHOP_EMAIL = "streamenglish@outlook.com"

CART_SESSION_ID = "cart"

# Shop Settings
SHOP_SETTINGS = {
    "GUEST_DOWNLOAD_EXPIRY_DAYS": 30,
    "MEMBER_DOWNLOAD_EXPIRY_DAYS": 365,
    "MAX_DOWNLOAD_ATTEMPTS": 3,
}

# Success URLs
LOGIN_REDIRECT_URL = "/profiles/profile/"
SHOP_SUCCESS_URL = "/shop/success/"
SHOP_CANCEL_URL = "/shop/cancel/"
