from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .helpers import set_user_group_from_role


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def assign_user_to_group(sender, instance, raw, **kwargs):
    if not raw:
        set_user_group_from_role(instance)