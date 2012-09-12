from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.conf import settings

from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authorization import Authorization
from guardian.shortcuts import get_objects_for_user, get_objects_for_group, get_users_with_perms, get_groups_with_perms
from lazy import lazy

from tweets.models import Tweet

everyone = Group.objects.get(name='Everyone')


class TweetResource(ModelResource):
    # created_by = fields.ForeignKey(UserRelatedResource, 'created_by', null=True)
    can_view = fields.ListField(readonly=True)
    can_edit = fields.ListField(readonly=True)
    is_admin = fields.ListField(readonly=True)
    group_can_view = fields.ListField(readonly=True)
    group_can_edit = fields.ListField(readonly=True)
    group_is_admin = fields.ListField(readonly=True)

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
                return get_objects_for_user(request.user, 'tweets.view_element', use_groups=True)
            else:
                return get_objects_for_group(everyone, 'tweets.view_element')

        elif request and request.method in ('DELETE'):
            # is_admin
            if request.user.is_authenticated() and request.user.is_active:
                return get_objects_for_user(request.user, 'tweets.admin_element', use_groups=True)
            else:
                return get_objects_for_group(everyone, 'tweets.admin_element')

        elif request and request.method in ('PUT', 'PATCH'):
            # can edit
            if request.user.is_authenticated() and request.user.is_active:
                return get_objects_for_user(request.user, 'tweets.edit_element', use_groups=True)
            else:
                return get_objects_for_group(everyone, 'tweets.edit_element')

    def dehydrate_can_view(self, bundle):
        return self.with_perm('view_element', bundle.obj, resource='user')

    def dehydrate_can_edit(self, bundle):
        return self.with_perm('edit_element', bundle.obj, resource='user')

    def dehydrate_is_admin(self, bundle):
        return self.with_perm('admin_element', bundle.obj, resource='user')

    def dehydrate_group_can_view(self, bundle):
        return self.with_perm('view_element', bundle.obj, resource='group')

    def dehydrate_group_can_edit(self, bundle):
        return self.with_perm('edit_element', bundle.obj, resource='group')

    def dehydrate_group_is_admin(self, bundle):
        return self.with_perm('admin_element', bundle.obj, resource='group')

    class Meta:
        queryset = Tweet.objects.all()  # this is ignored by get_object_list() above
        authorization = Authorization()
        read_only_fields = ['timestamp']  # ['created_by', 'timestamp']
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'delete', 'put']

#    @lazy
    def _users_with_perms(self, object):
        return get_users_with_perms(object, attach_perms=True, with_group_users=False)

#    @lazy
    def _groups_with_perms(self, object):
        return get_groups_with_perms(object, attach_perms=True)

    def with_perm(self, permission, object, resource):
        entity_uris = []
        if resource == 'group':
            entities_perms = self._groups_with_perms(object)
        else:
            entities_perms = self._users_with_perms(object)

        for entity in entities_perms.iterkeys():
            if permission in entities_perms[entity]:
                uri = reverse('api_dispatch_detail',
                              kwargs={'api_name': settings.API_VERSION,
                                      'pk': entity.pk,
                                      'resource_name': resource}
                )
                entity_uris.append(uri)

        return entity_uris