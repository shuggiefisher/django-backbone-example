from django.contrib.auth.models import User, Group
from django.conf import settings

from tastypie.resources import ModelResource
from tastypie.authorization import Authorization

class UserResource(ModelResource):

    class Meta:
        queryset = User.objects.all().exclude(pk=settings.ANONYMOUS_USER_ID)
        authorization = Authorization()
        fields = ['username']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']

class GroupResource(ModelResource):

    class Meta:
        queryset = Group.objects.all()
        authorization = Authorization()
        fields = ['name']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']