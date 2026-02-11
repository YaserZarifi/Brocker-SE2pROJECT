"""
Django settings for BourseChain project.
Sprint 2 - Backend API + Database
Sprint 3 - Matching Engine + Celery
Sprint 4 - Blockchain Integration
Sprint 5 - Real-time WebSocket + SIWE
Sprint 6 - Docker + Monitoring + DevOps
"""

import os
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-boursechain-dev-key-change-in-production-2026",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")


# =============================================================================
# Application definition
# =============================================================================

INSTALLED_APPS = [
    "daphne",  # Sprint 5: ASGI server for WebSocket support (must be before staticfiles)
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "channels",  # Sprint 5: Django Channels for WebSocket
    "django_prometheus",  # Sprint 6: Prometheus monitoring metrics
    # Local apps (Modular Monolith - each app = logical microservice)
    "users.apps.UsersConfig",
    "stocks.apps.StocksConfig",
    "orders.apps.OrdersConfig",
    "transactions.apps.TransactionsConfig",
    "notifications.apps.NotificationsConfig",
    "blockchain_service.apps.BlockchainServiceConfig",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",  # Sprint 6: Must be first
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Sprint 6: Serve static in production
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",  # Sprint 6: Must be last
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"  # Sprint 5: ASGI for WebSocket


# =============================================================================
# Database - PostgreSQL
# =============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "boursechain"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "postgres"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# For development without PostgreSQL, use SQLite:
if os.environ.get("USE_SQLITE", "False").lower() in ("true", "1", "yes"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# =============================================================================
# Cache - Redis
# =============================================================================

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# For development without Redis, use local memory cache:
if os.environ.get("USE_LOCMEM_CACHE", "False").lower() in ("true", "1", "yes"):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }


# =============================================================================
# Password validation
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# =============================================================================
# Internationalization
# =============================================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True


# =============================================================================
# Static files (CSS, JavaScript, Images)
# =============================================================================

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


# =============================================================================
# Default primary key field type
# =============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =============================================================================
# Custom User Model
# =============================================================================

AUTH_USER_MODEL = "users.User"


# =============================================================================
# Django REST Framework
# =============================================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
}


# =============================================================================
# Simple JWT Configuration
# =============================================================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}


# =============================================================================
# CORS Configuration (for Frontend at localhost:5173)
# =============================================================================

CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174",
).split(",")

CORS_ALLOW_CREDENTIALS = True


# =============================================================================
# drf-spectacular (API Documentation)
# =============================================================================

SPECTACULAR_SETTINGS = {
    "TITLE": "BourseChain API",
    "DESCRIPTION": "Online Stock Brokerage Platform - Amirkabir University SE2 Project",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}


# =============================================================================
# Celery Configuration (for Sprint 3)
# =============================================================================

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/2")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Tehran"

# For development without RabbitMQ: run Celery tasks synchronously (in-process).
# Automatically enabled when USE_SQLITE is True (dev mode), or set explicitly.
_use_eager = os.environ.get("CELERY_TASK_ALWAYS_EAGER", "").lower() in ("true", "1", "yes")
if not _use_eager and os.environ.get("USE_SQLITE", "False").lower() in ("true", "1", "yes"):
    _use_eager = True

CELERY_TASK_ALWAYS_EAGER = _use_eager
CELERY_TASK_EAGER_PROPAGATES = _use_eager  # Propagate exceptions in eager mode


# =============================================================================
# Blockchain Configuration (Sprint 4)
# =============================================================================

BLOCKCHAIN_ENABLED = os.environ.get("BLOCKCHAIN_ENABLED", "True").lower() in (
    "true",
    "1",
    "yes",
)
BLOCKCHAIN_RPC_URL = os.environ.get(
    "BLOCKCHAIN_RPC_URL", "http://127.0.0.1:8545"
)
# Hardhat Account #0 private key — well-known dev-only key, NOT a secret.
BLOCKCHAIN_PRIVATE_KEY = os.environ.get(
    "BLOCKCHAIN_PRIVATE_KEY",
    "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
)
# Set explicitly after deployment, or leave empty to read from contract_address.json
BLOCKCHAIN_CONTRACT_ADDRESS = os.environ.get("BLOCKCHAIN_CONTRACT_ADDRESS", "")


# =============================================================================
# Django Channels Configuration (Sprint 5 + Sprint 6)
# =============================================================================
# Dev: InMemoryChannelLayer (no Redis needed)
# Docker/Production: RedisChannelLayer (via Redis)

_use_inmemory_channel = os.environ.get("USE_LOCMEM_CACHE", "False").lower() in (
    "true",
    "1",
    "yes",
)

if _use_inmemory_channel:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [
                    os.environ.get(
                        "CHANNEL_REDIS_URL",
                        os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/3"),
                    )
                ],
            },
        }
    }


# =============================================================================
# SIWE (Sign-In with Ethereum) Configuration (Sprint 5)
# =============================================================================

SIWE_DOMAIN = os.environ.get("SIWE_DOMAIN", "localhost")
SIWE_URI = os.environ.get("SIWE_URI", "http://localhost:5173")


# =============================================================================
# Logging Configuration
# =============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "orders": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "blockchain_service": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "celery": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "notifications": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "stocks": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "users": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
