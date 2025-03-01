from unittest import TestCase
from src.utils.lru_cache import LRUCache

class TestObj:
    some: str

    def __init__(self, value: str):
        self.some = value

class TestLRUCache(TestCase):

    def test_create(self):
        cache = LRUCache(size=20)
        self.assertEqual(20, cache.size)
        self.assertEqual(0, cache.len)

    def test_put(self):
        cache = LRUCache(size=20)
        cache.put("aaa", "valulu")
        cache.put("aaa", "valula")
        cache.put("aaa", "valule")
        self.assertEqual(1, cache.len)

    def test_put_object(self):
        cache = LRUCache(size=20)
        cache.put("aaa", TestObj("valulu"))
        self.assertEqual(1, cache.len)

    def test_put_until_purge(self):
        cache = LRUCache(size=8, purge_ratio=0.5)
        for i in range(10):
            cache.put(f"k{i}{i}{i}", TestObj(f"v{i}{i}{i}"))
        self.assertEqual(6, cache.len)
        removed = cache.get(f"k111")
        self.assertIsNone(removed)
        existing = cache.get(f"k555")
        self.assertIsNotNone(existing)
        # get should have bumped the value
        self.assertEqual(existing.some, cache.stack.head.value.some)