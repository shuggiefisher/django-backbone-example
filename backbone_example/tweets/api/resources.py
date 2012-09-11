from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from guardian.shortcuts import get_objects_for_user, get_objects_for_group

from tweets.models import Tweet

everyone = Group.object.get(name='Everyone')

class TweetAuthorization(Authorization):

    def apply_limits(self, request, object_list=None):
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

        if isinstance(object_list, Bundle):  # 2.
            bundle = object_list
            bundle.data['created_by'] = {'pk': request.user.pk}  # 3.
            return bundle

        return []

class TweetResource(ModelResource):
    def obj_create(self, bundle, request, **kwargs):
        if request.user.is_authenticated() and request.user.is_active:
            user_pk = request.user.pk
        else:
            user_pk = None
        bundle.data['created_by'] = {'pk': user_pk}
        return super(TweetResource, self).obj_create(bundle, request, **kwargs)

    class Meta:
        queryset = Tweet.objects.all()
        authorization = TweetAuthorization()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'delete', 'put']
