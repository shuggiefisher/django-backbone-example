DEBUG = False
TEMPLATE_DEBUG = DEBUG
PIPELINE = not DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db'
    }
}

PORT = 80
HOSTNAME = 'interlist.co'