# In-Memory Caching 

#### Problem Statement
Design and Implement an in-memory caching library for general use
##### Must Have
- Support for multiple Standard Eviction Policies ( FIFO, LRU, LIFO )
- Support to add custom eviction policies
##### Good To Have
- Thread saftey

## Structure of the Project

The project consists of the following main components:
1. **eviction_policies.py**: It contains EvictionPolicy interface and standard eviction policy implementations (FIFO, LRU, LIFO).
2. **cache_metrics.py**: Implements metrics tracking for cache operations.
3. **cache.py**: Defines the core cache classes including CacheItem, Cache, and SegmentedCache.
4. **cache_factory.py**: Provides a CacheFactory class for creating instances of SegmentedCache with different eviction policies.
5. **demo.py**: This script demonstrates concurrent usage of your caching library with different eviction policies across multiple threads. It showcases basic cache operations, eviction handling, TTL functionality, and resizing of cache segments. Each thread operates independently on its own cache instance, demonstrating thread safety in accessing and manipulating the cache data structures.

## Assumptions
- All cache operations are performed in-memory. The cache is not designed to be persistent; all data is stored in memory and will be lost if the application terminates.
- To implement Custom eviction policy, user will create its own custom class implementing EvictionPolicy interface.
- Cache entries can have an optional TTL, after which they expire and are evicted from the cache.
- Expiry is checked during retrieval and put operations, but there is no background thread continuously purging expired items

## Approach

The library adopts an object-oriented approach with the following key design patterns:
- **Strategy Pattern**: Used in EvictionPolicy to define a family of interchangeable eviction algorithms.
- **Template Method Pattern**: Implemented in FIFOEvictionPolicy, LRUEvictionPolicy, and LIFOEvictionPolic to provide a skeleton of eviction algorithms with specific details left to subclasses.
- **Composite Pattern**: The Composite Pattern allows individual objects and compositions of objects to be treated uniformly. In the case of SegmentedCache, each segment can be considered an individual cache, and the entire SegmentedCache is a composition of these individual caches.
- **Factory Method Pattern**: Implemented in CacheFactory to encapsulate the creation of SegmentedCache instances based on client requirements.


# Class Overview

#### CacheItem
- **Attributes**: value, expiry
- **Methods**: None
- **Design Pattern**: None
- **Purpose**: Represents an item in the cache with value and optional expiration time.

#### CacheMetrics
- **Attributes**: hits, misses, total_requests, evictions, expirations, lock
- **Methods**: record_hit(), record_miss(), record_eviction(), record_expiration(), get_metrics()
- **Design Pattern**: None (uses Locking pattern)
- **Purpose**: Tracks and records cache performance metrics ensuring thread safety.

#### EvictionPolicy (Abstract Class)
- **Attributes**: None (abstract base class)
- **Methods**: add(key), remove(key), evict()
- **Design Pattern**: Strategy Pattern
- **Purpose**: Defines a common interface for different eviction policies.

#### FIFOEvictionPolicy, LRUEvictionPolicy, LIFOEvictionPolicy
- **Methods**: add(key), remove(key), evict()
- **Design Pattern**: Template Method Pattern (provides a skeleton of an algorithm).
- **Explanation**: Implements specific eviction policies using template methods for common eviction steps while leveraging subclass-specific data structures.
#### SegmentedCache
- **Attributes**: capacity_per_segment, eviction_policy_class, segments, eviction_policies, locks, metrics, num_segments, global_lock
- **Methods**: put(key, value, ttl), get(key), remove(key), _remove_expired_items(segment_index), _evict_item(segment_index), get_metrics(), resize_segments(new_num_segments)
- **Design Pattern**: Composite Pattern
- **Purpose**: Manages multiple cache segments with individual eviction policies ensuring thread-safe operations.

#### CacheFactory
- **Attributes**: _cache_types
- **Methods**: register_cache_type(cache_type, policy_class), create_cache(cache_type, capacity, num_segments)
- **Design Pattern**: Factory Method Pattern
- **Purpose**: Creates instances of SegmentedCache with specified eviction policies and configurations.


### Supporting Standard Eviction Policies

Standard eviction policies (FIFO, LRU, LIFO) are supported through dedicated classes FIFOEvictionPolicy, LRUEvictionPolicy, LIFOEvictionPolicy that encapsulate the specific eviction algorithms and data structures.

### Supporting Custom Eviction Policy

Custom eviction policies can be added by implementing the EvictionPolicy interface. The CacheFactory allows registration of custom eviction policies, enabling users to create SegmentedCache instances with these custom policies. For example we have mplement LFU (least frequently used ) eviction policy.

### Providing Thread Safety

Thread safety is ensured through the use of locks (Lock objects) in critical sections of cache operations within SegmentedCache and CacheMetrics. This prevents data races and maintains the integrity of cache operations in concurrent execution scenarios.

### Demo
To see the demo follow below steps:
- Clone the repo 
- Navigate to the repo directory
- run this command `python3 demo.py`. 


