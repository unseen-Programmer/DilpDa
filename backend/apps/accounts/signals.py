from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    CustomerProfile,
    DeliveryPartnerProfile,
    RestaurantOwnerProfile,
    User,
)


@receiver(post_save, sender=User)
def create_role_profile(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.role == User.Role.CUSTOMER:
        CustomerProfile.objects.get_or_create(user=instance)
    elif instance.role == User.Role.RESTAURANT_OWNER:
        RestaurantOwnerProfile.objects.get_or_create(user=instance)
    elif instance.role == User.Role.DELIVERY_PARTNER:
        DeliveryPartnerProfile.objects.get_or_create(user=instance)
