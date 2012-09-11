from tastypie.api import Api
from resources import TweetResource
from base.api.resources import UserResource

v1 = Api("v1")
v1.register(TweetResource(), UserResource())
