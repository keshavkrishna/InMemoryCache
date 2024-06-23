from typing import Type
from cache import SegmentedCache
from eviction_policies import EvictionPolicy, FIFOEvictionPolicy, LRUEvictionPolicy, LIFOEvictionPolicy

class CacheFactory:
    _cache_types = {
        "FIFO": FIFOEvictionPolicy,
        "LRU": LRUEvictionPolicy,
        "LIFO": LIFOEvictionPolicy
    }

    @classmethod
    def register_cache_type(cls, cache_type: str, policy_class: Type[EvictionPolicy]):
        cls._cache_types[cache_type] = policy_class

    @classmethod
    def create_cache(cls, cache_type: str, capacity: int, num_segments: int = 16):
        policy_class = cls._cache_types.get(cache_type)
        if policy_class is None:
            raise ValueError(f"Unsupported cache type: {cache_type}")
        return SegmentedCache(capacity, policy_class, num_segments)