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


# -----------------------------------------------------------------------------
# Database (SQLite)
# -----------------------------------------------------------------------------
# Database - SQLite default for Docker. Use in production
# DATABASES = {"default": env.db(default="sqlite:////app/db/db.sqlite3")}

# Database - SQLite. Use in development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "data" / "db" / "db.sqlite3",
    }
}


# -----------------------------------------------------------------------------
# Apps
# -----------------------------------------------------------------------------

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

# -----------------------------------------------------------------------------
# Auth
# -----------------------------------------------------------------------------

LOGIN_URL = "/profiles/login/"
LOGIN_REDIRECT_URL = "/profiles/dashboard/"
LOGOUT_REDIRECT_URL = "/"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]


# -----------------------------------------------------------------------------
# Templates
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# Internationalization
# -----------------------------------------------------------------------------

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# Static / Media
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# Sessions
# -----------------------------------------------------------------------------
# SESSION_ENGINE = "django.contrib.sessions.backends.db"
# SESSION_COOKIE_NAME = "sessionid"
# SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 1 week
# SESSION_SAVE_EVERY_REQUEST = True
# SESSION_COOKIE_PATH = "/"

# if DEBUG:
#     SESSION_COOKIE_SAMESITE = "Lax"
#     SESSION_COOKIE_SECURE = False
#     SESSION_COOKIE_HTTPONLY = True
# else:
#     SESSION_COOKIE_SECURE = True
#     SESSION_COOKIE_HTTPONLY = True


# Site configuration
SITE_ID = 2

# -----------------------------------------------------------------------------
# Security (production)
# -----------------------------------------------------------------------------
# if not DEBUG:
#     SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
#     SECURE_SSL_REDIRECT = True
#     SECURE_HSTS_SECONDS = 31536000
#     SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#     SECURE_HSTS_PRELOAD = True
#     SECURE_CONTENT_TYPE_NOSNIFF = True
#     SECURE_BROWSER_XSS_FILTER = True
#     X_FRAME_OPTIONS = "DENY"
#     USE_X_FORWARDED_HOST = True
#     USE_X_FORWARDED_PORT = True

# # Rate limiting (login security)
# IP_RATE_LIMIT_TIMEOUT = 120
# IP_RATE_LIMIT_MAX_ATTEMPTS = 10  # adjust based on your middleware

# -----------------------------------------------------------------------------
# Site / shop
# -----------------------------------------------------------------------------
SITE_NAME = "Stream English"
SITE_URL = env(
    "SITE_URL",
    default=("http://localhost:8000" if DEBUG else "https://streamenglish.co.uk"),
)

CART_SESSION_ID = "cart"

# -----------------------------------------------------------------------------
# Stripe
# -----------------------------------------------------------------------------
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY", default="pk_test_placeholder")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="sk_test_placeholder")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="whsec_placeholder")

# -----------------------------------------------------------------------------
# Email + verification
# -----------------------------------------------------------------------------
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@streamenglish.co.uk")

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)

EMAIL_VERIFICATION_TOKEN_EXPIRY = 36  # hours

PASSWORD_RESET_TIMEOUT = 3600


# -----------------------------------------------------------------------------
# TinyMCE
# -----------------------------------------------------------------------------
TINYMCE_DEFAULT_CONFIG = {
    "height": 700,
    "menubar": False,
    "statusbar": True,
    "branding": False,
    "plugins": "lists paste link autolink code preview fullscreen wordcount image",
    "toolbar": (
        "undo redo | blocks | bold italic | bullist numlist | "
        "link image | removeformat | preview fullscreen | code"
    ),
    "block_formats": "Paragraph=p; Heading 2=h2; Heading 3=h3",
    "forced_root_block": "p",
    "paste_as_text": True,
    "paste_data_images": False,
    "valid_elements": (
        "p,strong/b,em/i,h2,h3,ul,ol,li,a[href|title|target|rel],br,"
        "img[src|alt|width|height|class|style]"
    ),
    "extended_valid_elements": (
        "a[href|title|target|rel],img[src|alt|width|height|class|style]"
    ),
    "valid_children": "+ol[li],+ul[li]",
    "convert_urls": True,
    "relative_urls": False,
    "remove_script_host": False,
    "content_style": (
        "body{font-family:Poppins,system-ui,sans-serif;line-height:1.7;}"
        "h2{font-size:1.5rem;font-weight:700;margin:1rem 0 .5rem;}"
        "h3{font-size:1.25rem;font-weight:600;margin:.75rem 0 .25rem;}"
        "p{margin:.75rem 0;} ul,ol{margin:.5rem 0 1rem;padding-left:1.25rem;}"
        "li{margin:.25rem 0;} strong{font-weight:600;}"
        "img{max-width:100%;height:auto;display:block;margin:1rem auto;}"
    ),
    "image_dimensions": False,
    "image_class_list": [
        {"title": "Responsive (50%)", "value": "img-half"},
        {"title": "Full width", "value": "img-full"},
    ],
}

# -----------------------------------------------------------------------------
# Logging (optional)
# -----------------------------------------------------------------------------

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
