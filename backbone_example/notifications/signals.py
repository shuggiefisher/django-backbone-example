from django.db.models.signals import post_save
from django.dispatch import receiver

from tweets.models import Tweet

import logging
log = logging.getLogger(__name__)

@receiver(post_save, sender=Tweet)
def create_alerts(sender, instance, created, raw, **kwargs):
    if not raw:
        # if dirty_fields includes message