# settings.py
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# Seguridad / Debug
# -----------------------------
SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-^#af8u5i7(&hjgz5gmhf%f43l!7@ge+je6vevv%)s$nex3uz(c",
)
DEBUG = config("DEBUG", cast=bool, default=True)

# Comas: "localhost,127.0.0.1,*.onrender.com"
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    cast=Csv(),               # lee "a,b,c" -> ["a","b","c"]
    default="localhost,127.0.0.1"
)

# Confía en el proxy de Render para detectar HTTPS correcto
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Si usas Render, agrega: CSRF_TRUSTED_ORIGINS=https://<tu-servicio>.onrender.com
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", cast=Csv(), default="")

# -----------------------------
# Apps
# -----------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "hotel",
]

# -----------------------------
# Middleware (con WhiteNoise)
# -----------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # ← WhiteNoise justo después de SecurityMiddleware
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
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# -----------------------------
# Base de datos
# -----------------------------
# Opción explícita vía variable DB_ENGINE:
#   - DB_ENGINE=sqlite  → usa SQLite (default) en BASE_DIR/db.sqlite3 (sin cambios)
#   - DB_ENGINE=postgres → usa Postgres con las variables:
#       POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT
DB_ENGINE = config("DB_ENGINE", default="sqlite").lower()

if DB_ENGINE == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("POSTGRES_DB"),
            "USER": config("POSTGRES_USER"),
            "PASSWORD": config("POSTGRES_PASSWORD"),
            "HOST": config("POSTGRES_HOST", default="localhost"),
            "PORT": config("POSTGRES_PORT", default="5432"),
            # Si tu proveedor exige SSL (p. ej. Render/Neon), activa DB_SSL_REQUIRE=true
            "OPTIONS": {"sslmode": "require"} if config("DB_SSL_REQUIRE", cast=bool, default=False) else {},
        }
    }
else:
    # Predeterminado: como lo tienes ahora mismo
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# -----------------------------
# Passwords
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------
# I18N
# -----------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = config("TIME_ZONE", default="UTC")
USE_I18N = True
USE_TZ = True

# -----------------------------
# Static (WhiteNoise)
# -----------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Archivos comprimidos + hash para cache busting
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -----------------------------
# PK por defecto
# -----------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
