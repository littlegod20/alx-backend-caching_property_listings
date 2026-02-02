from django.core.cache import cache
from .models import Property


def get_all_properties():
    """
    Get all properties from cache or database.
    Caches the queryset in Redis for 1 hour (3600 seconds).
    """
    # Check Redis for cached properties
    cached_properties = cache.get('all_properties')
    
    if cached_properties is not None:
        return cached_properties
    
    # If not in cache, fetch from database
    properties = Property.objects.all()
    
    # Store in Redis cache for 1 hour (3600 seconds)
    cache.set('all_properties', properties, 3600)
    
    return properties
