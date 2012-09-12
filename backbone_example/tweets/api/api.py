from tastypie.api import Api
from resources import TweetResource
from base.api.resources import UserResource, GroupResource
from django.conf import settings

v1 = Api(settings.API_VERSION)
v1.register(TweetResource())
v1.register(UserResource())
v1.register(GroupResource())
