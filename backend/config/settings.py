from datetime import timedelta
import os, ssl, re
from pathlib import Path
import dj_database_url


import environ  # import environ

env = environ.Env()  # Initialise environment variables
environ.Env.read_env()




# import environ  # import environ

# env = environ.Env()  # Initialise environment variables
# environ.Env.read_env()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# Declared in your environment variables
IS_HEROKU = "DYNO" in os.environ
IS_GITHUB = "GITHUB_WORKFLOW" in os.environ
# REDIS_URL = os.environ.get('REDIS_URL')
if IS_HEROKU or IS_GITHUB:
    DEBUG = False
    SECRET_KEY = os.environ['SECRET_KEY']
    RAPID_API = os.environ['RAPID_API']
    EMAIL_HOST_PASSWORD = os.environ['EMAIL_PASSWD']
    SCRAPFLY_KEY = os.environ['SCRAPFLY_KEY']
    ST_APP_KEY = os.environ['ST_APP_KEY']
    SALESFORCE_CONSUMER_KEY = os.environ['SALESFORCE_CONSUMER_KEY']
    SALESFORCE_CONSUMER_SECRET = os.environ['SALESFORCE_CONSUMER_SECRET']
    CELERY_RESULT_BACKEND = os.environ['REDIS_URL']
    BASE_FRONTEND_URL = 'https://app.ismycustomermoving.com'
    BASE_BACKEND_URL = 'https://is-my-customer-moving.herokuapp.com'
    GOOGLE_OAUTH2_CLIENT_ID = os.environ['GOOGLE_OAUTH2_CLIENT_ID']
    GOOGLE_OAUTH2_CLIENT_SECRET = os.environ['GOOGLE_OAUTH2_CLIENT_SECRET']
    
else:
    DEBUG = True
    SECRET_KEY = env('SECRET_KEY')
    RAPID_API = env('RAPID_API')
    EMAIL_HOST_PASSWORD = env('EMAIL_PASSWD')
    SCRAPFLY_KEY = env('SCRAPFLY_KEY')
    ST_APP_KEY = env('ST_APP_KEY')
    SALESFORCE_CONSUMER_KEY = env('SALESFORCE_CONSUMER_KEY')
    SALESFORCE_CONSUMER_SECRET = env('SALESFORCE_CONSUMER_SECRET')
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    BASE_FRONTEND_URL = 'http://localhost:3000'
    BASE_BACKEND_URL = 'http://localhost:8000'
    GOOGLE_OAUTH2_CLIENT_ID = env('GOOGLE_OAUTH2_CLIENT_ID')
    GOOGLE_OAUTH2_CLIENT_SECRET = env('GOOGLE_OAUTH2_CLIENT_SECRET')

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", "is-my-customer-moving.herokuapp.com"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',

    # To generate Admin Docs  Requirement -> # pip install docutils
    'django.contrib.admindocs',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Native Apps
    'accounts.apps.AccountsConfig',
    'payments.apps.PaymentsConfig',
    'data.apps.DataConfig',

    # 3rd Party
    'rest_framework',  # https://www.django-rest-framework.org/
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',  # To Connect API with React App if required in seprate apps
    'django_rest_passwordreset',
    'djstripe',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # new
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]

# Auth user
AUTH_USER_MODEL = "accounts.CustomUser"

# Configure django-rest-framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    # 'DEFAULT_THROTTLE_CLASSES': [
    #     'rest_framework.throttling.AnonRateThrottle',
    #     'rest_framework.throttling.UserRateThrottle'
    # ],
    # 'DEFAULT_THROTTLE_RATES': {
    #     'anon': '100/day',
    #     'user': '1000/day'
    # }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=60),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),

    'AUTH_COOKIE': 'IMCM_Cookie',
}


ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# this part will be executed if IS_POSTGRESQL = False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

MAX_CONN_AGE = 600

if "DATABASE_URL" in os.environ:
    # Configure Django for DATABASE_URL environment variable.
    DATABASES["default"] = dj_database_url.config(
        conn_max_age=MAX_CONN_AGE, ssl_require=True)

    # Enable test database if found in CI environment.
    if "CI" in os.environ:
        DATABASES["default"]["TEST"] = DATABASES["default"]
# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


PASSWORD_HASHERS = [
    # python -m pip install argon2-cffi
    # https://docs.djangoproject.com/en/3.2/topics/auth/passwords/#using-argon2-with-django
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',

]
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3006",
    "http://localhost:3007",  # React App will be on this port
    "https://is-my-customer-moving.vercel.app",
    "https://ismycustomermoving.com",
    "https://www.ismycustomermoving.com",
    "https://app.ismycustomermoving.com",

    # Stripe
    "https://3.18.12.63",
    "https://3.130.192.231",
    "https://13.235.14.237",
    "https://13.235.122.149",
    "https://18.211.135.69",
    "https://35.154.171.200",
    "https://52.15.183.38",
    "https://54.88.130.119",
    "https://54.88.130.237",
    "https://54.187.174.169",
    "https://54.187.205.235",
    "https://54.187.216.72",
]


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = "smtp.gmail.com" # Your SMTP Provider or in this case gmail
EMAIL_PORT = 587
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ['EMAIL']
ACCOUNT_EMAIL_VERIFICATION = 'none'
#assigned at the beginning
# EMAIL_HOST_PASSWORD

CELERY_BROKER_URL = os.environ.get('REDIS_URL')
CELERY_TIMEZONE = 'US/Central'
CELERYD_TASK_TIME_LIMIT= 10
CELERY_TASK_RESULT_EXPIRES = 10


CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL')],
        },
    },
}


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get('REDIS_URL'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # "CONNECTION_POOL_KWARGS": {
            #     "ssl_cert_reqs": ssl.CERT_NONE,
            # },
        }
    }
}

STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
STRIPE_PUBLISHABLE_KEY_TEST = os.environ.get('STRIPE_PUBLIC_KEY_TEST')


STRIPE_LIVE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_TEST_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY_TEST")
STRIPE_LIVE_MODE = True

DJSTRIPE_WEBHOOK_SECRET = "whsec_N8LMT9fUTcrtlEBvKaHLKTnXWLE2uybj"
DJSTRIPE_FOREIGN_KEY_TO_FIELD = "id"

DJSTRIPE_WEBHOOK_VALIDATION='retrieve_event'