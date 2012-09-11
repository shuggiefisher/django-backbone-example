from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.dispatch import receiver

import logging
log = logging.getLogger(__name__)

@receiver(post_save, User)
def add_user_to_everyone_group(sender, instance, created, raw, **kwargs):
    if raw is False:
        if created is True:
            everyone = Group.objects.get(name='Everyone')
            everyone.add_member(instance)