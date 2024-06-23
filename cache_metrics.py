from threading import Lock

class CacheMetrics:
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.total_requests = 0
        self.evictions = 0
        self.expirations = 0
        self.lock = Lock()

    def record_hit(self):
        with self.lock:
            self.hits += 1
            self.total_requests += 1

    def record_miss(self):
        with self.lock:
            self.misses += 1
            self.total_requests += 1

    def record_eviction(self):
        with self.lock:
            self.evictions += 1

    def record_expiration(self):
        with self.lock:
            self.expirations += 1

    def get_metrics(self):
        with self.lock:
            return {
                "hits": self.hits,
                "misses": self.misses,
                "total_requests": self.total_requests,
                "evictions": self.evictions,
                "expirations": self.expirations,
                "hit_ratio": self.hits / self.total_requests if self.total_requests > 0 else 0,
                "miss_ratio": self.misses / self.total_requests if self.total_requests > 0 else 0
            }