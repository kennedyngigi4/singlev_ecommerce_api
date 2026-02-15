
from django.dispatch import receiver
from django.db.models.signals import post_save

from apps.accounts.models.models import User
from apps.accounts.models.customer_profile import CustomerProfile, CustomerLocation


@receiver(post_save, sender=User)
def create_profile_account(created, instance, *args, **kwargs):

    if created:
        if instance.role == "client":
            CustomerProfile.objects.create(user=instance)

