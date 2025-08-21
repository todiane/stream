from pathlib import Path
import environ
import os
import sys


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
logs_dir = BASE_DIR / "logs"
env = environ.Env()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Choose environment file
ENV_FILE = ".env"
environ.Env.read_env(os.path.join(BASE_DIR, ENV_FILE))

COLLECT_STATIC = "collectstatic" in sys.argv

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="your-secret-key-here")

# Database configuration
DATABASES = {
    "default": {
        "ENGINE": "mysql.connector.django",
        "NAME": env("DATABASE_NAME"),
        "USER": env("DATABASE_USER"),
        "PASSWORD": env("DATABASE_PASSWORD"),
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


DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "localhost:8000"]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:8000",
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
    "redirects",
]

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
                "django.template.context_processors.media",
                "shop.context_processors.cart",
            ],
        },
    },
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "stream.middleware.csrf_debug.CSRFDebugMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "redirects.middleware.RedirectMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "profiles.middleware.IPRateLimitMiddleware",
    "middleware.error_handling.ErrorHandlingMiddleware",
]

SITE_ID = 1

SITE_URL = "http://127.0.0.1:8000"

# How many tries before we throttle
# IP_RATE_LIMIT_MAX_ATTEMPTS = 1000

# How long (in seconds) to block an IP once it exceeds the max
# IP_RATE_LIMIT_TIMEOUT = 300000


ROOT_URLCONF = "stream.urls"

WSGI_APPLICATION = "stream.wsgi.application"


# email settings to be implemented:

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "localhost"  # Using local mail server
EMAIL_PORT = 25  # Standard SMTP port
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
CONTACT_EMAIL = env("CONTACT_EMAIL")

# Add these explicit settings

EMAIL_TIMEOUT = 30  # Timeout in seconds
EMAIL_MAX_RETRIES = 3
SERVER_EMAIL = env("DEFAULT_FROM_EMAIL")

# Account activation settings
ACCOUNT_ACTIVATION_DAYS = 7  # One-week activation window
ACCOUNT_ACTIVATION_LINK_EXPIRED_HOURS = 24 * ACCOUNT_ACTIVATION_DAYS
REGISTRATION_SALT = "registration"

# Security settings for password reset
PASSWORD_RESET_TIMEOUT = 259200  # 3 days in seconds
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]


# Login/logout settings
LOGIN_REDIRECT_URL = "/profiles/profile/"
LOGIN_URL = "/profiles/login/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/profiles/login/"

# Stripe settings
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY", default="")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="")
STRIPE_CURRENCY = "gbp"

# Shop Email
SHOP_EMAIL = "info@streamenglish.co.uk"

# logging error emails
SERVER_EMAIL = "no-reply@streamenglish.co.uk"

CART_SESSION_ID = "cart"

# Shop Settings
SHOP_SETTINGS = {
    "GUEST_DOWNLOAD_EXPIRY_DAYS": 30,
    "MEMBER_DOWNLOAD_EXPIRY_DAYS": 365,
    "MAX_DOWNLOAD_ATTEMPTS": 3,
}

# Success URLs
SHOP_SUCCESS_URL = "/shop/success/"
SHOP_CANCEL_URL = "/shop/cancel/"

# Admin notification settings
ADMINS = [
    ("Admin", "no-reply@streamenglish.co.uk"),
]

# Media and Storage Configuration
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
PUBLIC_MEDIA_ROOT = os.path.join(MEDIA_ROOT, "public")
SECURE_MEDIA_ROOT = os.path.join(MEDIA_ROOT, "secure_downloads")
MEDIA_PREFIX = "public/"

MEDIA_FILE_SERVE_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Cache-Control": "no-cache, must-revalidate",
}

# File Permissions
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Storage Configuration
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": MEDIA_ROOT,
            "base_url": MEDIA_URL,
            "file_permissions_mode": FILE_UPLOAD_PERMISSIONS,
            "directory_permissions_mode": FILE_UPLOAD_DIRECTORY_PERMISSIONS,
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Cache Control Headers for Media Files
MEDIA_FILE_STORAGE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
}

# Create directories if they don't exist
for directory in [MEDIA_ROOT, PUBLIC_MEDIA_ROOT, SECURE_MEDIA_ROOT]:
    os.makedirs(directory, exist_ok=True)

# Static files configuration
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# Add secure storage settings
SECURE_DOWNLOADS_URL = (
    "/downloads/"  # This will be handled by a view, not direct access
)

# WhiteNoise configuration

WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False


# Ensure consistent handling of URLs
CKEDITOR_UPLOAD_SLUGIFY_FILENAME = True
CKEDITOR_JQUERY_URL = None
CKEDITOR_FILENAME_GENERATOR = "utils.get_filename_generator"

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_ALLOW_NONIMAGE_FILES = True
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"
CKEDITOR_RESTRICT_BY_USER = True
CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
        "height": 300,
        "width": "100%",
        "removePlugins": "stylesheetparser",
        "extraPlugins": ",".join(
            [
                "uploadimage",
                "image2",
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
        "filebrowserUploadUrl": "/ckeditor/upload/",
        "filebrowserBrowseUrl": "/ckeditor/browse/",
        "contentsCss": [
            "p { margin: 0.5em 0; }",
            "h1, h2, h3, h4, h5, h6 { font-family: 'Lato', sans-serif; }",
        ],
        "enterMode": 2,
        "shiftEnterMode": 1,
        "format_tags": "p;h1;h2;h3;pre",
        "removeDialogTabs": "image:advanced;link:advanced",
        "stylesSet": [
            {
                "name": "Paragraph",
                "element": "p",
                "attributes": {"style": "margin: 0.5em 0;"},
            },
            {
                "name": "Heading 1",
                "element": "h1",
                "attributes": {"style": "font-family: 'Lato', sans-serif;"},
            },
            {
                "name": "Heading 2",
                "element": "h2",
                "attributes": {"style": "font-family: 'Lato', sans-serif;"},
            },
            {
                "name": "Heading 3",
                "element": "h3",
                "attributes": {"style": "font-family: 'Lato', sans-serif;"},
            },
        ],
    },
}


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
