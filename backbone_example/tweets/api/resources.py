from tastypie.resources import ModelResource
from tastypie.authorization import Authorization

from tweets.models import Tweet

class TweetResource(ModelResource):
    def obj_create(self, bundle, request, **kwargs):
        if request.user.is_authenticated() and request.user.is_active:
            user_pk = request.user.pk
        else:
            user_pk = None
        bundle.data['created_by'] = {'pk': user_pk}
        return super(BlogPostResource, self).obj_create(bundle, request, **kwargs)

    class Meta:
#        exclude = (('created_by'),)
        queryset = Tweet.objects.all()
        authorization = Authorization()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'delete', 'put']
