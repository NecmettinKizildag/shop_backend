from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product
from django.core.cache import cache

@receiver([post_save, post_delete], sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    """
    Invalidate the cache for the product list when a product is created, updated, or deleted.
    """
    print(f"Clearing product cache")
    #cache.delete_pattern('*product_list*')