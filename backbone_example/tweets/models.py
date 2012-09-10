from django.db import models

class Tweet(models.Model):
    message = models.CharField(max_length=140)
    timestamp = models.DateTimeField(auto_now_add=True)
    # created_by = models.ForeignKey('auth.User')
    type = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        permissions = (
            ('view_element', 'Can view element'),
            ('edit_element', 'Can edit element'),
            ('admin_element', 'Is admin of element'),
        )
