import threading
import time
from cache_factory import CacheFactory
from eviction_policies import EvictionPolicy
from typing import Generic, TypeVar, Dict
from collections import defaultdict

K = TypeVar('K')

#  declared this class to implement LFU (least frequently used ) eviction policy
class LFUEvictionPolicy(EvictionPolicy, Generic[K]):
    def __init__(self):
        self.key_frequency: Dict[K, int] = defaultdict(int)
        self.frequency_keys: Dict[int, set[K]] = defaultdict(set)
        self.min_frequency = 0

    def add(self, key: K) -> None:
        if key not in self.key_frequency:
            self.key_frequency[key] = 1
            self.frequency_keys[1].add(key)
            self.min_frequency = 1
        else:
            self._increment_frequency(key)

    def remove(self, key: K) -> None:
        if key in self.key_frequency:
            freq = self.key_frequency[key]
            self.frequency_keys[freq].remove(key)
            if len(self.frequency_keys[freq]) == 0:
                del self.frequency_keys[freq]
                if freq == self.min_frequency:
                    self.min_frequency += 1
            del self.key_frequency[key]

    def evict(self) -> K:
        if not self.key_frequency:
            raise ValueError("No keys to evict")
        
        key_to_evict = next(iter(self.frequency_keys[self.min_frequency]))
        self.remove(key_to_evict)
        return key_to_evict

    def _increment_frequency(self, key: K) -> None:
        freq = self.key_frequency[key]
        self.key_frequency[key] = freq + 1
        self.frequency_keys[freq].remove(key)
        if len(self.frequency_keys[freq]) == 0:
            del self.frequency_keys[freq]
            if freq == self.min_frequency:
                self.min_frequency += 1
        self.frequency_keys[freq + 1].add(key)




def test_cache(cache, thread):
    # Put some items in the cache
    for i in range(4):
        cache.put(f"key{i}", f"value{i}")
        print(f"{thread} Added key{i}")

    # Access some items multiple times to increase their frequency
    for _ in range(3):
        cache.get("key0")
    for _ in range(2):
        cache.get("key1")
    
    print(f"\n {thread} Current cache state:")
    for i in range(4):
        try:
            print(f" {thread} key{i}: {cache.get(f'key{i}')}")
        except KeyError:
            print(f" {thread} key{i}: NOt found")

    

    for i in range(4, 16):
        cache.put(f"key{i}", f"value{i}")
        print(f"{thread} Added key{i}")
    
    print(f"\n {thread} Afteer adding more items:")
    for i in range(16):
        try:
            print(f" {thread} key{i}: {cache.get(f'key{i}')}")
        except KeyError:
            print(f" {thread} key{i}: Not found")

    # Resize the segment, add one more segment
    cache.resize_segments(cache.num_segments + 1)


    print(f"\n {thread} After ading one mre dsegment:")
    for i in range(6):
        try:
            print(f" {thread} key{i}: {cache.get(f'key{i}')}")
        except KeyError:
            print(f" {thread} key{i}: Not found")

    # Demonstrate TTL functionality
    cache.put("ttl_key", "ttl_value", ttl=2)
    print(f"\n {thread} After adding ttl_key:")
    print(f"{thread} ttl_key: {cache.get('ttl_key')}")

    time.sleep(3)

    print(f"\n {thread} After waiting for TTL expiristion:")
    try:
        print(f"{thread} ttl_key: {cache.get('ttl_key')}")
    except KeyError:
        print(f"{thread} ttl_key: expired")


    # Print cache metrics
    print(f"\n {thread} Cache Metrics:")
    print(cache.get_metrics())



def create_test_cache(thread, cache_type, capacity, num_segments):
    cache = CacheFactory.create_cache(cache_type, capacity=capacity, num_segments=num_segments)
    test_cache(cache, thread)

def main():
    threads = []

    # Create a thread for each cache operation
    threads.append(threading.Thread(target=create_test_cache, args=("Thread1->", "FIFO", 3, 4)))
    threads.append(threading.Thread(target=create_test_cache, args=("Thread2->", "LRU", 3, 2)))
    threads.append(threading.Thread(target=create_test_cache, args=("Thread3->", "LIFO", 3, 3)))

    # have implemented the custom class LFUEvictionPolicy to add custom Eviction policy, 
    # it will basically replicate Least frequently Used policy to evict 
    CacheFactory.register_cache_type("LFU", LFUEvictionPolicy)
    threads.append(threading.Thread(target=create_test_cache, args=("Thread4->", "LFU", 3, 4)))

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait till all the  threads are  completed
    for thread in threads:
        thread.join()

   

if __name__ == "__main__":
    main()
