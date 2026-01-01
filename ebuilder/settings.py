from pathlib import Path
import environ
from django.core.exceptions import DisallowedHost

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment setup
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, []),
)
env.read_env(BASE_DIR / ".env")

# Security settings
SECRET_KEY = env("SECRET_KEY", default="unsafe-secret-key-change-in-production")
DEBUG = env("DEBUG")
SITE_URL = "https://www.djangify.com"

ALLOWED_HOSTS = [
    "djangify.com",
    "www.djangify.com",
    "localhost",
    "127.0.0.1",
    "corrisonapi.com",
]


# CSRF and CORS - read from environment with sensible defaults
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS") or [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://djangify.com",
    "https://www.djangify.com",
]


CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS") or [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://djangify.com",
    "https://www.djangify.com",
]


# Application definition
INSTALLED_APPS = [
    "adminita",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.redirects",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "accounts",
    "infopages",
    "blog",
    "shop",
    "pages",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "widget_tweaks",
    "tinymce",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ebuilder.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "shop.context_processors.cart",
                "pages.context_processors.ebuilder_settings",
                "pages.context_processors.published_pages",
                "pages.context_processors.site_settings",
                "pages.context_processors.home_url",
                "pages.context_processors.current_site",
                "pages.context_processors.dashboard_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "ebuilder.wsgi.application"


# Database - SQLite default for Docker. Use in production
DATABASES = {"default": env.db(default="sqlite:////app/db/db.sqlite3")}


# Database - SQLite. Use in development
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

# Custom User Model
AUTH_USER_MODEL = "accounts.User"

# Allauth Configuration
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = [
    "email*",
    "first_name*",
    "last_name*",
    "password1*",
    "password2*",
]
ACCOUNT_ADAPTER = "accounts.adapters.CustomAccountAdapter"

LOGIN_REDIRECT_URL = "/accounts/dashboard/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/accounts/login/"

ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files (digital products)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# WhiteNoise Configuration
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# Cache static files for 1 year (immutable because of hashed filenames)
WHITENOISE_MAX_AGE = 31536000  # 1 year in seconds

# Stripe settings
STRIPE_PUBLIC_KEY = env("STRIPE_PUBLIC_KEY", default="pk_test_placeholder")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="sk_test_placeholder")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="whsec_placeholder")

CART_SESSION_ID = "cart"
ADMIN_EMAIL = env("ADMIN_EMAIL", default="admin@example.com")

# Cookie security - set to True in production with HTTPS
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=False)


# Email settings - defaults to console for easy local development
EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)

# Email settings for production
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="mail.privateemail.com")  # noqa: F405
EMAIL_PORT = env("EMAIL_PORT", default=587)  # noqa: F405
EMAIL_HOST_USER = env("EMAIL_HOST_USER")  # noqa: F405
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")  # noqa: F405
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="djangify@djangify.com")

# =============================================================================
# TINYMCE CONFIGURATION (Self-hosted, FREE plugins only)
# =============================================================================

TINYMCE_DEFAULT_CONFIG = {
    # Core settings
    "height": 500,
    "menubar": "file edit view insert format tools table help",
    "branding": False,  # Removes "Powered by TinyMCE"
    "promotion": False,  # Removes upgrade prompts
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
# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Create logs directory path
LOG_DIR = BASE_DIR / "data" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "disable_disallowed_host": {
            "()": "ebuilder.settings.DisableDisallowedHostEmails",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
        },
        "file_error": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "django-error.log",
            "maxBytes": 5 * 1024 * 1024,  # 5 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "file_debug": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "django-debug.log",
            "maxBytes": 5 * 1024 * 1024,  # 5 MB
            "backupCount": 3,
            "formatter": "simple",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
            "filters": ["disable_disallowed_host"],
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file_error", "mail_admins"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["file_error", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

# =============================================================================
# EMAIL CONFIGURATION (for error notifications)
# =============================================================================

ADMINS = [
    ("Diane", env("ADMIN_EMAIL", default="your-email@example.com")),
]

# Email backend - use SMTP for production
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="smtp.example.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@example.com")
SERVER_EMAIL = env("SERVER_EMAIL", default="errors@example.com")


IGNORABLE_404_URLS = [
    r"^/echo\.php",
]


class DisableDisallowedHostEmails:
    def filter(self, record):
        if record.exc_info:
            exc_type, exc, tb = record.exc_info
            return not isinstance(exc, DisallowedHost)
        return True
