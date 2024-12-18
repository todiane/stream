from pathlib import Path
import environ
import os
import sys
from .logging_config import LOGGING


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Load environment variables from .env file
# Choose environment file
ENV_FILE = (
    ".env.local" if os.path.exists(os.path.join(BASE_DIR, ".env.local")) else ".env"
)
print(f"Using environment file: {os.path.join(BASE_DIR, ENV_FILE)}")
environ.Env.read_env(os.path.join(BASE_DIR, ENV_FILE))


COLLECT_STATIC = "collectstatic" in sys.argv

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="your-secret-key-here")


# Database configuration
DATABASES = {
    "default": {
        "ENGINE": "mysql.connector.django",
        "NAME": env("DATABASE_NAME", default="str3a3eng24-3530303000b6"),
        "USER": env("DATABASE_USER", default="str3a3eng24-3530303000b6"),
        "PASSWORD": env("DATABASE_PASSWORD", default=""),
        "HOST": env("DATABASE_HOST", default="127.0.0.1"),
        "PORT": env("DATABASE_PORT", default="3306"),
        "OPTIONS": {
            "charset": "latin1",
            "use_unicode": True,
            "connect_timeout": 10,
            "autocommit": True,
        },
    },
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
    "ckeditor",
    "ckeditor_uploader",
    "simple_history",
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
    "middleware.error_handling.ErrorHandlingMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
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

# media and static settings
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
PUBLIC_MEDIA_ROOT = os.path.join(MEDIA_ROOT, "public")
SECURE_MEDIA_ROOT = os.path.join(MEDIA_ROOT, "secure_downloads")

# Create directories if they don't exist
for directory in [MEDIA_ROOT, PUBLIC_MEDIA_ROOT, SECURE_MEDIA_ROOT]:
    os.makedirs(directory, exist_ok=True)

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

# WhiteNoise configuration
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False


if DEBUG:
    INSTALLED_APPS += ["whitenoise.runserver_nostatic"]
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_AUTOREFRESH = True
    WHITENOISE_MANIFEST_STRICT = False

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


# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = env("SENDGRID_API_KEY", default="")
SENDGRID_API_KEY = env("SENDGRID_API_KEY", default=None)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
CONTACT_EMAIL = env("CONTACT_EMAIL")


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

# Stripe settings
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLIC_KEY", default="")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="")

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


# Admin notification settings
ADMINS = [
    ("Admin", "streamenglish@outlook.com"),
]

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
        "height": 300,
        "width": "100%",
        "removePlugins": "stylesheetparser",
        "extraPlugins": ",".join(
            [
                "uploadimage",
                "image2",  # Enhanced image plugin
                "autolink",
                "autoembed",
                "embedsemantic",
                "autogrow",
                "widget",
                "lineutils",
                "clipboard",
                "dialog",
                "dialogui",
                "elementspath",
            ]
        ),
        "uploadUrl": "/ckeditor/upload/",
    },
}
