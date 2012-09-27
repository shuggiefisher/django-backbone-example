from django.views.generic.base import TemplateView
from django.http import Http404

from api import v1
from .models import Tweet

class IndexView(TemplateView):
    template_name = 'test.html'

    def get_users_and_groups(self):
        ur = v1.canonical_resource_for('user')
        users_bundles = self._get_list_for_resource(ur)

        gr = v1.canonical_resource_for('group')
        groups_bundles = self._get_list_for_resource(gr)

        return dict(users=users_bundles, groups=groups_bundles)


    def _get_list_for_resource(self, resource):
        instances = resource.cached_obj_get_list()
        sorted_instances = resource.apply_sorting(instances)
        bundles = [resource.build_bundle(obj=obj, request=None) for obj in sorted_instances]
        bundle_data = [resource.full_dehydrate(bundle).data for bundle in bundles]
        return bundle_data

    def get_context_data(self, **kwargs):
        base = super(IndexView, self).get_context_data(**kwargs)
        base['users_and_groups'] = self.get_users_and_groups()
        return base

class DetailView(IndexView):
    template_name = 'test.html'

    def get_detail(self, pk):
        tr = v1.canonical_resource_for('tweet')

        try:
            tweet = tr.cached_obj_get(pk=pk)
        except Tweet.DoesNotExist:
            raise Http404

        bundle = tr.full_dehydrate(tr.build_bundle(obj=tweet))
        data = bundle.data
        return data

    def get_context_data(self, **kwargs):
        base = super(DetailView, self).get_context_data(**kwargs)
        base['data'] = self.get_detail(base['params']['pk'])
        return base
