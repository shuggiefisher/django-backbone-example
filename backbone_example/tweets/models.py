from django.db import models
from django.contrib.auth.models import Group

from guardian.shortcuts import assign
from mptt.models import MPTTModel, TreeManyToManyField


class Tweet(models.Model):
    message = models.CharField(max_length=140)
    timestamp = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', null=True)
    type = models.CharField(max_length=30, null=True, blank=True)
    parents = TreeManyToManyField('self', related_name='children')

    class MPTTMeta:
        permissions = (
            ('view_element', 'Can view element'),
            ('edit_element', 'Can edit element'),
            ('admin_element', 'Is admin of element'),
        )

    def __unicode__(self):
        return unicode("%s : %s : %s" % (self.pk, self.created_by, self.message))

    def save(self, *args, **kwargs):
        if self.pk is None:
            created = True
        else:
            created = False

        # pre_save

        super(Tweet, self).save(*args, **kwargs)

        # post_save
        if created is True:
            # make it readable and editable by everyone by default
            everyone = Group.objects.get(name='Everyone')
            assign('view_element', everyone, self)
            assign('edit_element', everyone, self)
            if self.created_by is not None:
                assign('admin_element', self.created_by, self)
            else:
                assign('admin_element', everyone, self)

