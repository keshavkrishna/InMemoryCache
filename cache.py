from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Dict, Any
from threading import Lock
from time import time
from eviction_policies import EvictionPolicy
from cache_metrics import CacheMetrics

K = TypeVar('K')
V = TypeVar('V')

class CacheItem:
    def __init__(self, value: Any, expiry: Optional[float] = None):
        self.value = value
        self.expiry = expiry

class Cache(ABC, Generic[K, V]):
    @abstractmethod
    def put(self, key: K, value: V, ttl: Optional[int] = None) -> None:
        pass

    @abstractmethod
    def get(self, key: K) -> V:
        pass

    @abstractmethod
    def remove(self, key: K) -> None:
        pass

    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        pass

class SegmentedCache(Cache[K, V]):
    def __init__(self, capacity_per_segment: int, eviction_policy_class: EvictionPolicy[K], num_segments: int = 16):
        self.capacity_per_segment = capacity_per_segment
        self.eviction_policy_class = eviction_policy_class
        self.segments = [{} for _ in range(num_segments)]  # Each segment is a dictionary
        self.eviction_policies = [eviction_policy_class() for _ in range(num_segments)]  # Instantiate policy for each segment
        self.locks = [Lock() for _ in range(num_segments)]  # One lock per segment
        self.metrics = CacheMetrics()
        self.num_segments = num_segments
        self.global_lock = Lock()

    def _get_segment(self, key: K) -> int:
        return hash(key) % self.num_segments

    def put(self, key: K, value: V, ttl: Optional[int] = None) -> None:
        segment_index = self._get_segment(key)
        with self.locks[segment_index]:
            self._remove_expired_items(segment_index)
            if key in self.segments[segment_index]:
                self.eviction_policies[segment_index].remove(key)
            elif len(self.segments[segment_index]) >= self.capacity_per_segment:
                self._evict_item(segment_index)
            
            expiry = time() + ttl if ttl is not None else None
            self.segments[segment_index][key] = CacheItem(value, expiry)
            self.eviction_policies[segment_index].add(key)

    def get(self, key: K) -> V:
        segment_index = self._get_segment(key)
        with self.locks[segment_index]:
            self._remove_expired_items(segment_index)
            if key not in self.segments[segment_index]:
                self.metrics.record_miss()
                raise KeyError(f"Key '{key}' not found in cache")
            
            item = self.segments[segment_index][key]
            if item.expiry is not None and item.expiry <= time():
                del self.segments[segment_index][key]
                self.eviction_policies[segment_index].remove(key)
                self.metrics.record_expiration()
                self.metrics.record_miss()
                raise KeyError(f"Key '{key}' has expired")
            
            self.eviction_policies[segment_index].remove(key)
            self.eviction_policies[segment_index].add(key)
            self.metrics.record_hit()
            return item.value

    def remove(self, key: K) -> None:
        segment_index = self._get_segment(key)
        with self.locks[segment_index]:
            if key in self.segments[segment_index]:
                del self.segments[segment_index][key]
                self.eviction_policies[segment_index].remove(key)

    def _remove_expired_items(self, segment_index: int) -> None:
        current_time = time()
        expired_keys = [k for k, v in self.segments[segment_index].items() if v.expiry is not None and v.expiry <= current_time]
        for key in expired_keys:
            del self.segments[segment_index][key]
            self.eviction_policies[segment_index].remove(key)
            self.metrics.record_expiration()

    def _evict_item(self, segment_index: int) -> None:
        evicted_key = self.eviction_policies[segment_index].evict()
        del self.segments[segment_index][evicted_key]
        self.metrics.record_eviction()

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics.get_metrics()

    def resize_segments(self, new_num_segments: int) -> None:
        if new_num_segments <= 0:
            raise ValueError("Number of segments must be positive")
        
        acquired_locks = []
        with self.global_lock:
            current_num_segments = self.num_segments
            for lock in self.locks:
                lock.acquire()
                acquired_locks.append(lock)

            try:
                if new_num_segments > current_num_segments:
                    self.segments.extend([{} for _ in range(new_num_segments - current_num_segments)])
                    self.eviction_policies.extend([self.eviction_policy_class() for _ in range(new_num_segments - current_num_segments)])
                    self.locks.extend([Lock() for _ in range(new_num_segments - current_num_segments)])
                elif new_num_segments < current_num_segments:
                    self.segments = self.segments[:new_num_segments]
                    self.eviction_policies = self.eviction_policies[:new_num_segments]
                    self.locks = self.locks[:new_num_segments]

                self.num_segments = new_num_segments
                print(f"Segments resized to {new_num_segments}")

            finally:
                for lock in acquired_locks:
                    lock.release()

    def __str__(self) -> str:
        return f"SegmentedCache with {self.num_segments} segments, capacity per segment: {self.capacity_per_segment}"
