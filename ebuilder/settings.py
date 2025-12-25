from pathlib import Path
import environ

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
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
SITE_URL = env("SITE_URL", default="http://localhost:8000")

# CSRF and CORS - read from environment with sensible defaults
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS") or [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS") or [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
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


# Database - SQLite default
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Custom User Model
AUTH_USER_MODEL = "accounts.User"

# Allauth Configuration
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = [
    "email*",
    "first_name*",
    "password1*",
    "password2*",
]
# ACCOUNT_ADAPTER = "accounts.adapters.CustomAccountAdapter"

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

# SMTP settings only loaded if using SMTP backend
if EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend":
    EMAIL_HOST = env("EMAIL_HOST", default="localhost")
    EMAIL_PORT = env.int("EMAIL_PORT", default=587)
    EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
    EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
    EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@example.com")


# TinyMCE Configuration
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
