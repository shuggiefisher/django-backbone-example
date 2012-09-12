from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.dispatch import receiver

from tweets.api.resources import everyone
from tweets.models import Tweet

import logging
log = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def add_user_to_everyone_group(sender, instance, created, raw, **kwargs):
    if raw is False:
        if created is True:
            everyone.user_set.add(instance)
            me = Tweet(message=instance.username, type="person")
            me.save()