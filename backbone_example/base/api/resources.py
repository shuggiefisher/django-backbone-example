from django.contrib.auth.models import User, Group
from django.conf import settings
from django.conf.urls.defaults import url

from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie import fields


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


class MeResource(ModelResource):
    api_key = fields.CharField()
    registered = fields.BooleanField()

    def override_urls(self):
        """
        No need to pass any pk arguments to this resource
        """

        return [
            url(r"^(?P<resource_name>%s)/$" % self._meta.resource_name, self.wrap_view('dispatch_list'), name="api_dispatch_list"),
        ]

    def obj_get(self, request=None, **kwargs):
        """
        Override GETs to ensure that a user can only get their own details
        """
        if request.user.is_anonymous():
            return super(MeResource, self).obj_get(request=None, pk=settings.ANONYMOUS_USER_ID)
        else:
            return super(MeResource, self).obj_get(request=None, pk=request.user.pk)

    def dehydrate_api_key(self, bundle):
        return bundle.obj.api_key.key

    def dehydrate_registered(self, bundle):
        if bundle.obj.pk == settings.ANONYMOUS_USER_ID:
            return False
        else:
            return True

    class Meta:
        resource_name = 'me'
        queryset = User.objects.all()
        authorization = Authorization()
        fields = ['username', 'id']
        list_allowed_methods = ['get']