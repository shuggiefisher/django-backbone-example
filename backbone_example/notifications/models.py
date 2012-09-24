from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Alert(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    alerted_by = models.ForeignKey('users.User')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return unicode("%s : %s : %s" % (self.created_at, self.alerted_by, self.content_object.message))

class Notification(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    alert = models.ForeignKey('notifications.Alert')
    body = models.TextField(null=False)