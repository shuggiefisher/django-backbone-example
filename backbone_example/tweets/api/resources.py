from django.contrib.auth.models import Group

from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from guardian.shortcuts import get_objects_for_user, get_objects_for_group

from tweets.models import Tweet

everyone = Group.objects.get(name='Everyone')


class TweetResource(ModelResource):

    def __init__(self, **kwargs):
        super(TweetResource, self).__init__(**kwargs)
        for fieldname in getattr(self.Meta, 'read_only_fields', []):
            self.fields[fieldname].readonly = True

    def obj_create(self, bundle, request, **kwargs):
        if request.user.is_authenticated() and request.user.is_active:
            user_pk = request.user.pk
        else:
            user_pk = None
        bundle.data['created_by'] = {'pk': user_pk}
        return super(TweetResource, self).obj_create(bundle, request, **kwargs)

    def get_object_list(self, request):
        """
        This is effectively doing the authorization, so it may result in incorrect
        HTTP status codes being produced
        """
        if request and request.method in ('GET'):
            # can view
            if request.user.is_authenticated() and request.user.is_active:
                return get_objects_for_user(request.user, 'tweets.view_element')
            else:
                return get_objects_for_group(everyone, 'tweets.view_element')

        elif request and request.method in ('DELETE'):
            # is_admin
            if request.user.is_authenticated() and request.user.is_active:
                return get_objects_for_user(request.user, 'tweets.admin_element')
            else:
                return get_objects_for_group(everyone, 'tweets.admin_element')

        elif request and request.method in ('PUT', 'PATCH'):
            # can edit
            if request.user.is_authenticated() and request.user.is_active:
                return get_objects_for_user(request.user, 'tweets.edit_element')
            else:
                return get_objects_for_group(everyone, 'tweets.edit_element')

    class Meta:
        queryset = Tweet.objects.all()  # this is ignored by get_object_list() above
        authorization = Authorization()
        read_only_fields = ['created_by', 'timestamp']
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'delete', 'put']
