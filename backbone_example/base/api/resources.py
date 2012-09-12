from django.contrib.auth.models import User, Group

from tastypie.resources import ModelResource
from tastypie.authorization import Authorization

class UserResource(ModelResource):

    class Meta:
        queryset = User.objects.all()
        authorization = Authorization()
        fields = ['username']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']

class GroupResource(ModelResource):

    class Meta:
        queryset = Group.objects.all()
        authorization = Authorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']