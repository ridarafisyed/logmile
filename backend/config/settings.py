from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: list[str]) -> list[str]:
    value = os.getenv(name)
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


def sqlite_path_config() -> Path:
    sqlite_path = os.getenv("SQLITE_PATH")
    if not sqlite_path:
        return BASE_DIR / "db.sqlite3"

    configured_path = Path(sqlite_path)
    if configured_path.is_absolute():
        return configured_path

    return BASE_DIR / configured_path


def database_config() -> dict[str, str | Path]:
    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": sqlite_path_config(),
    }


def cache_config() -> dict[str, dict[str, str]]:
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        return {
            "default": {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": redis_url,
                "TIMEOUT": env_int("DJANGO_CACHE_DEFAULT_TIMEOUT", 300),
            }
        }

    return {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "logmile-local-cache",
            "TIMEOUT": env_int("DJANGO_CACHE_DEFAULT_TIMEOUT", 300),
        }
    }


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = env_bool("DJANGO_DEBUG", env_bool("DEBUG", True))
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", ["localhost", "127.0.0.1"])


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "trips",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


DATABASES = {
    "default": database_config()
}

CACHES = cache_config()

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "EXCEPTION_HANDLER": "trips.exceptions.api_exception_handler",
    "DEFAULT_THROTTLE_RATES": {
        "location_search": os.getenv("LOCATION_SEARCH_RATE", "180/min"),
        "trip_plan_burst": os.getenv("TRIP_PLAN_BURST_RATE", "12/min"),
        "trip_plan_sustained": os.getenv("TRIP_PLAN_SUSTAINED_RATE", "1000/day"),
    },
}


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


LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    env_list(
        "CORS_ORIGINS",
        [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
    ),
)

OPENROUTESERVICE_API_KEY = os.getenv(
    "OPENROUTESERVICE_API_KEY",
    os.getenv("ORS_API_KEY", ""),
)
ORS_REQUEST_TIMEOUT_SECONDS = env_int("ORS_REQUEST_TIMEOUT_SECONDS", 20)
ORS_MAX_RETRIES = env_int("ORS_MAX_RETRIES", 3)
MAPS_CACHE_TTL_SECONDS = env_int("MAPS_CACHE_TTL_SECONDS", 86400)

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", [])

SPECTACULAR_SETTINGS = {
    "TITLE": "LogMile API",
    "DESCRIPTION": (
        "Backend API for trip planning, HOS calculations, route data, "
        "and ELD log generation."
    ),
    "VERSION": "1.0.0",
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "trips": {
            "handlers": ["console"],
            "level": os.getenv("TRIPS_LOG_LEVEL", "INFO"),
            "propagate": False,
        }
    },
}
