import logging
from django.core.cache import cache
from django_redis import get_redis_connection
from .models import Property

logger = logging.getLogger(__name__)


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


def get_redis_cache_metrics():
    """
    Retrieve and analyze Redis cache hit/miss metrics.
    Returns a dictionary with hits, misses, and hit ratio.
    """
    try:
        # Connect to Redis via django_redis
        redis_conn = get_redis_connection("default")
        
        # Get INFO command results
        info = redis_conn.info('stats')
        
        # Get keyspace_hits and keyspace_misses
        keyspace_hits = info.get('keyspace_hits', 0)
        keyspace_misses = info.get('keyspace_misses', 0)
        
        # Calculate hit ratio (hits / (hits + misses))
        total_requests = keyspace_hits + keyspace_misses
        if total_requests > 0:
            hit_ratio = keyspace_hits / total_requests
        else:
            hit_ratio = 0.0
        
        # Create metrics dictionary
        metrics = {
            'keyspace_hits': keyspace_hits,
            'keyspace_misses': keyspace_misses,
            'total_requests': total_requests,
            'hit_ratio': hit_ratio,
        }
        
        # Log metrics
        logger.info(
            f"Redis Cache Metrics - Hits: {keyspace_hits}, "
            f"Misses: {keyspace_misses}, "
            f"Hit Ratio: {hit_ratio:.2%}"
        )
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error retrieving Redis cache metrics: {str(e)}")
        return {
            'keyspace_hits': 0,
            'keyspace_misses': 0,
            'total_requests': 0,
            'hit_ratio': 0.0,
            'error': str(e)
        }
