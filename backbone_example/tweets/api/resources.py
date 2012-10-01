from django.contrib.auth.models import Group, User
from django.core.urlresolvers import reverse
from django.conf import settings

from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie import http
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.utils import dict_strip_unicode_keys
from guardian.shortcuts import get_objects_for_user, get_objects_for_group, \
    get_users_with_perms, get_groups_with_perms, remove_perm, assign
from lazy import lazy

from tweets.models import Tweet
from base.api.resources import UserResource

everyone = Group.objects.get(pk=settings.EVERYONE_GROUP_ID)
anonymous_user = User.objects.get(pk=settings.ANONYMOUS_USER_ID)


class TweetResource(ModelResource):
    created_by = fields.ForeignKey(UserResource, 'created_by', null=True)
    can_view = fields.ListField()
    can_edit = fields.ListField()
    is_admin = fields.ListField()
    group_can_view = fields.ListField()
    group_can_edit = fields.ListField()
    group_is_admin = fields.ListField()
    can_edit_permissions = fields.BooleanField()
    can_edit_element = fields.BooleanField()

    def __init__(self, **kwargs):
        super(TweetResource, self).__init__(**kwargs)
        for f in getattr(self.Meta, 'readonly_fields', []):
            self.fields[f].readonly = True

    def obj_create(self, bundle, request, **kwargs):
        if request.user.is_authenticated() and request.user.is_active:
            user_pk = request.user
        else:
            user_pk = None
        bundle.data['created_by'] = user_pk
        return super(TweetResource, self).obj_create(bundle, request, **kwargs)

    def obj_update(self, bundle, request, **kwargs):
        self.fields['created_by'].readonly = True
        bundle = super(TweetResource, self).obj_update(bundle, request, **kwargs)
        self.update_permissions(bundle, request.user)
        return bundle

    def put_detail(self, request, **kwargs):
        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
        self.is_valid(bundle, request)

        updated_bundle = self.obj_update(bundle, request=request, **self.remove_api_resource_names(kwargs))

        if not self._meta.always_return_data:
            return http.HttpNoContent()
        else:
            updated_bundle = self.full_dehydrate(updated_bundle)
            updated_bundle = self.alter_detail_data_to_serialize(request, updated_bundle)
            return self.create_response(request, updated_bundle, response_class=http.HttpAccepted)

    def get_object_list(self, request):
        """
        This is effectively doing the authorization, so it may result in incorrect
        HTTP status codes being produced
        """
        if request.user.is_anonymous():
            requesting_user = anonymous_user
        else:
            requesting_user = request.user

        if request and request.method in ('GET'):
            # can view
            return get_objects_for_user(requesting_user, 'tweets.view_element', use_groups=True)

        elif request and request.method in ('DELETE'):
            # is_admin
            return get_objects_for_user(requesting_user, 'tweets.admin_element', use_groups=True)

        elif request and request.method in ('PUT', 'PATCH'):
            # can edit
            return get_objects_for_user(requesting_user, 'tweets.edit_element', use_groups=True)

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

    def dehydrate_group_is_admin(self, bundle):
        return self.with_perm('admin_element', bundle.obj, resource='group')

    def dehydrate_can_edit_permissions(self, bundle):
        if bundle.request.user.is_anonymous():
            requesting_user = anonymous_user
        else:
            requesting_user = bundle.request.user

        return requesting_user.has_perm('admin_element', bundle.obj)

    def dehydrate_can_edit_element(self, bundle):
        if bundle.request.user.is_anonymous():
            requesting_user = anonymous_user
        else:
            requesting_user = bundle.request.user

        return requesting_user.has_perm('edit_element', bundle.obj)

    class Meta:
        queryset = Tweet.objects.all()  # this is ignored by get_object_list() above
        authorization = Authorization()
#        readonly_fields = ['timestamp'] don't use this because value will be ignored anyway
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'delete', 'put']
        always_return_data = True  # helps integration with backbone which respects a response on POSTs

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
                if resource == 'group':
                    entity_name = entity.name
                else:
                    entity_name = entity.username

                entity_uris.append({'name': entity_name,
                                    'resource_uri': uri
                })

        return entity_uris

    def update_permissions(self, bundle, editing_user):
        if editing_user.has_perm('tweets.admin_element', bundle.obj) is False:
            return
            # bundle has already been saved, so no point in raising an error
#            raise ImmediateHttpResponse(response=http.HttpUnauthorized('Only admins of an element can change the permissions'))

        self._update_user_permissions(bundle)
        self._update_group_permissions(bundle)

    def _update_group_permissions(self, bundle):
        groups_with_perms = self._groups_with_perms(bundle.obj)
        resource_permissions = ['group_can_view', 'group_can_edit', 'group_is_admin']
        self._update_perms(bundle, groups_with_perms, resource_permissions, Group)

    def _update_user_permissions(self, bundle):
        users_with_perms = self._users_with_perms(bundle.obj)
        resource_permissions = ['can_view', 'can_edit', 'is_admin']
        self._update_perms(bundle, users_with_perms, resource_permissions, User)

    def _update_perms(self, bundle, entities_with_perms, resource_permissions, entity_model):
        permissions = ['view_element', 'edit_element', 'admin_element']
        for permission, resource_permission in zip(permissions, resource_permissions):

            perm_pairs = bundle.data[resource_permission]  # get data for this permission from bundle
            perm_uris = [perm_pair['resource_uri'] for perm_pair in perm_pairs]  # get the resource_uris
            new_entity_pks = [int(uri.rstrip('/').split('/')[-1]) for uri in perm_uris]  # get the resource pks

            # get the pks of groups or users currently with this permission on this obj
            current_entity_pks = [entity.pk for entity in entities_with_perms.iterkeys() if permission in entities_with_perms[entity]]

            entities_to_add = set(new_entity_pks) - set(current_entity_pks)
            entities_to_remove = set(current_entity_pks) - set(new_entity_pks)

            for entity in entity_model.objects.filter(pk__in=entities_to_remove):
                remove_perm(permission, entity, bundle.obj)
                if resource_permission == 'is_admin':
                    if set(current_entity_pks) - entities_to_remove == set() and entities_to_add == set():
                        # if everyone else is removed, the original author or everyone should remain the admin
                        if bundle.obj.created_by is None:
                            default_admin = everyone
                        else:
                            default_admin = bundle.obj.created_by
                        assign(permission, default_admin, bundle.obj)

            for entity in entity_model.objects.filter(pk__in=entities_to_add):
                assign(permission, entity, bundle.obj)