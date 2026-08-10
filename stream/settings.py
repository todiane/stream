# stream/settings.py

from pathlib import Path
import os
import environ

# -----------------------------------------------------------------------------
# Paths + env
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment setup
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, []),
)
env.read_env(str(BASE_DIR / ".env"))
# -----------------------------------------------------------------------------
# Core
# -----------------------------------------------------------------------------
SECRET_KEY = env("SECRET_KEY", default="unsafe-secret-key-change-in-production")
DEBUG = env("DEBUG")
SITE_URL = env("SITE_URL", default="http://localhost:8000")


# CSRF and CORS - read from environment with sensible defaults
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://streamenglish.co.uk",
        "https://www.streamenglish.co.uk",
    ],
)


CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "https://streamenglish.co.uk",
        "https://www.streamenglish.co.uk",
    ],
)


ALLOWED_HOSTS = [
    "streamenglish.co.uk",
    "www.streamenglish.co.uk",
    "mail.streamenglish.co.uk",
    "localhost",
    "127.0.0.1",
]


# ------------------------------------------------------------
# Database (SQLite)
# ------------------------------------------------------------
# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ----------------------------------------------------------
# Apps
# ----------------------------------------------------------

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "courses",
    "profiles",
    "shop",
    "news",
    "pages",
    "redirects",
    "widget_tweaks",
    "tinymce",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "profiles.middleware.IPRateLimitMiddleware",
]

ROOT_URLCONF = "stream.urls"
WSGI_APPLICATION = "stream.wsgi.application"

# ---------------------------------------------------------------
# Auth
# ----------------------------------------------------------

LOGIN_URL = "/profiles/login/"
LOGIN_REDIRECT_URL = "/profiles/profile/"
LOGOUT_REDIRECT_URL = "/"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]


# -------------------------------------------------------
# Templates
# --------------------------------------------------------
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
                "pages.context_processors.site_settings",
            ],
        },
    },
]

# -----------------------------------------------------------------------------
# Password validation
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------------------------------------
# Internationalization
# ---------------------------------------------------------

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------
# Static / Media
# ------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


SESSION_COOKIE_SAMESITE = "Lax"
# SECURE_SSL_REDIRECT below forces HTTPS in production, so cookies should
# only ever be sent over HTTPS too - this was hardcoded to False, which
# meant session/CSRF cookies weren't marked "Secure" even in production.
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG

# Site configuration
SITE_ID = 2

# This was hardcoded to True, which forces every request onto HTTPS -
# including local development (DEBUG=True), where the dev server only
# serves plain HTTP. That meant `runserver` would 301-redirect every request
# to an https:// URL that doesn't exist locally. Only force it in production.
SECURE_SSL_REDIRECT = not DEBUG

# ----------------------------------------------------------
# Site / shop
# --------------------------------------------------------
SITE_NAME = "Stream English"
SITE_URL = env(
    "SITE_URL",
    default=("http://localhost:8000" if DEBUG else "https://streamenglish.co.uk"),
)

CART_SESSION_ID = "cart"

# -------------------------------------------------------
# Stripe
# --------------------------------------------------------
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY", default="pk_test_placeholder")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="sk_test_placeholder")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="whsec_placeholder")

# --------------------------------------------------------------
# Email + verification
# -------------------------------------------------------------
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@streamenglish.co.uk")
# CONTACT_EMAIL was set in .env but never actually read into a Django
# setting - every submission of the contact form (profiles.views.contact_tutor)
# and the tuition booking form (courses.views.booking_form_view) referenced
# settings.CONTACT_EMAIL and raised an AttributeError, so neither form's
# email ever actually sent.
CONTACT_EMAIL = env("CONTACT_EMAIL", default=DEFAULT_FROM_EMAIL)
ACCOUNT_ACTIVATION_DAYS = env.int("ACCOUNT_ACTIVATION_DAYS", default=7)

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)

EMAIL_VERIFICATION_TOKEN_EXPIRY = 36  # hours

PASSWORD_RESET_TIMEOUT = 3600


# ======================================================
# TINYMCE CONFIGURATION (Self-hosted, FREE plugins only)
# =====================================================

TINYMCE_DEFAULT_CONFIG = {
    # Core settings
    "height": 500,
    "menubar": "file edit view insert format tools table help",
    "branding": False,
    "promotion": False,
    # FREE plugins only - no premium plugins = no console errors
    "plugins": [
        "advlist",  # Advanced list formatting
        "autolink",  # Auto-convert URLs to links
        "lists",  # Bullet and numbered lists
        "link",  # Insert/edit links
        "image",  # Insert/edit images
        "charmap",  # Special characters
        "preview",  # Preview content
        "anchor",  # Named anchors
        "searchreplace",  # Find and replace
        "visualblocks",  # Show block elements
        "code",  # Edit HTML source
        "fullscreen",  # Fullscreen editing
        "insertdatetime",  # Insert date/time
        "media",  # Embed videos
        "table",  # Tables
        "wordcount",  # Word count
        "help",  # Help dialog
    ],
    # Toolbar configuration
    "toolbar": (
        "undo redo | blocks | bold italic underline strikethrough | "
        "alignleft aligncenter alignright alignjustify | "
        "bullist numlist outdent indent | link image media table | "
        "code fullscreen preview | removeformat help"
    ),
    # Block formats (headings, paragraph, etc.)
    "block_formats": "Paragraph=p; Heading 2=h2; Heading 3=h3; Heading 4=h4; Blockquote=blockquote; Code=pre",
    # Image settings - allows upload and URL
    "image_advtab": True,
    "image_caption": True,
    "automatic_uploads": True,
    "file_picker_types": "image",
    "images_upload_url": "/tinymce/upload/",  # We'll create this view
    # Link settings
    "link_default_target": "_blank",
    "link_assume_external_targets": True,
    # Content styling - uses your site's CSS
    "content_css": "/static/css/tinymce-content.css",
    # Clean paste from Word
    "paste_as_text": False,
    # Security - what HTML is allowed
    "valid_elements": (
        "p,br,b,strong,i,em,u,s,strike,sub,sup,"
        "h1,h2,h3,h4,h5,h6,"
        "ul,ol,li,"
        "a[href|target|title],"
        "img[src|alt|title|width|height|class],"
        "table[border|cellspacing|cellpadding],thead,tbody,tr,th[colspan|rowspan],td[colspan|rowspan],"
        "blockquote,pre,code,"
        "div[class],span[class],"
        "hr"
    ),
    # Relative URLs (important for portability)
    "relative_urls": False,
    "remove_script_host": True,
    "document_base_url": "/",
}

# ---------------------------------------------------------
# Logging (optional)
# ----------------------------------------------------------

ADMINS = [("Diane", "dcorriette@gmail.com")]

# Logging - production level
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["file", "console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
