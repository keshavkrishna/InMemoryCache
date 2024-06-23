from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from collections import OrderedDict

K = TypeVar('K')

class EvictionPolicy(ABC, Generic[K]):
    @abstractmethod
    def add(self, key: K) -> None:
        pass

    @abstractmethod
    def remove(self, key: K) -> None:
        pass

    @abstractmethod
    def evict(self) -> K:
        pass

class FIFOEvictionPolicy(EvictionPolicy[K]):
    def __init__(self):
        self.queue = []

    def add(self, key: K) -> None:
        self.queue.append(key)

    def remove(self, key: K) -> None:
        self.queue.remove(key)

    def evict(self) -> K:
        return self.queue.pop(0)

class LRUEvictionPolicy(EvictionPolicy[K]):
    def __init__(self):
        self.order = OrderedDict()

    def add(self, key: K) -> None:
        self.order[key] = None

    def remove(self, key: K) -> None:
        if key in self.order:
            del self.order[key]

    def evict(self) -> K:
        return self.order.popitem(last=False)[0]

class LIFOEvictionPolicy(EvictionPolicy[K]):
    def __init__(self):
        self.stack = []

    def add(self, key: K) -> None:
        self.stack.append(key)

    def remove(self, key: K) -> None:
        self.stack.remove(key)

    def evict(self) -> K:
        return self.stack.pop()