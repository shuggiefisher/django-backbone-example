# Django settings for backbone_example project.
import os

PROJECT_ROOT = os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'backbone_example.db'
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT,'media')
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'collected_static')
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

STATIC_URL = "/static/"

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '637i_o@27q89j^-gm+i!5g4#&pwo%)^^m&2g@4o^a8f92l#klq'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'django.core.context_processors.request',
)

ROOT_URLCONF = 'backbone_example.urls'

TEMPLATE_DIRS = (
  os.path.join(PROJECT_ROOT, "templates"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'guardian',
    'django_extensions',
    'social_auth',

    'base',
    'tweets'
)

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'django.contrib.auth.backends.ModelBackend',  # this is default
    'guardian.backends.ObjectPermissionBackend',
)

ANONYMOUS_USER_ID = 1

API_VERSION = 'v1'

LOGIN_URL          = '/login-form/'
LOGIN_REDIRECT_URL = '/logged-in/'
LOGIN_ERROR_URL    = '/login-error/'

TWITTER_CONSUMER_KEY         = '7O7YUzfuIYUBm7zA6K1xQA'
TWITTER_CONSUMER_SECRET      = 'aYl5l930PGx1N97YxUreJH1YT1jxZAGAhCCCNT1g'

TWITTER_ACCESS_TOKEN         = '331027719-89VXUFOHMYcSu0rUlaNuquY9O48jFgcyNy4a6QnS'
TWITTER_ACCESS_TOKEN_SECRET  = '75vPhfdzRwqMdnBRfofkCpMIJAnh7dvf7Fx32eDRg8'

TWITTER_EXTRA_DATA = [
    ('screen_name', 'screen_name'),
    ('profile_image_url', 'profile_image_url'),
    ('geo_enabled', 'geo_enabled'),
    ('followers_count', 'followers_count'),
    ('default_profile_image', 'default_profile_image'),
    ('utc_offset', 'utc_offset'),
    ('statuses_count', 'statuses_count'),
    ('friends_count', 'friends_count'),
    ('url', 'url'),
    ('location', 'location'),
    ('protected', 'protected')
]