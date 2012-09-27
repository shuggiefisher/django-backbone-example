from django.core.urlresolvers import reverse
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings

from manifesto import Manifest


class StaticManifest(Manifest):
    def cache(self):

        if settings.DEBUG is False:
            return [
                reverse('index'),
                staticfiles_storage.url('js/mobile.js'),
                staticfiles_storage.url('css/mobile.css'),
            ]
        else:
            # in debug mode we don't want anything to go in the application cache
            return []

    # def fallback(self):
    #     return [
    #       ('','/offline.html'),
    #     ]