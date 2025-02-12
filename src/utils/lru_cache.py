from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from doubly_list import DLL, T, Node

class LRUItem(BaseModel):
    key: str
    value: T
    node: Node

    class Config:
        json_encoders = {}

class LRUCache(BaseModel):
    """ Least Recently Used (LRU) O(1) Cache """

    # # dic holds the actual items
    dic: Dict[str, LRUItem] = None
    # # stack only tracks item keys
    stack: DLL = None
    size: int
    purge_ratio: float

    # size 0 for unlimited
    # must be 0 < purge_ratio <= 1
    def __init__(self, /, size: int = 0, purge_ratio: float = .25, **data: Any) -> None:
        super().__init__(size=size, purge_ratio=purge_ratio, **data)
        assert size > 0
        assert size < 1024
        assert purge_ratio > 0
        assert purge_ratio <= 1
        self.size = size
        self.stack = DLL(size=size)
        self.dic = {}
        self.purge_ratio = purge_ratio

    @property
    def len(self) -> int:
        return self.stack.len

    def __have_vacancy__(self) -> bool:
        """is there room for one more?"""
        return self.stack.len < self.size

    def __pop__(self) -> T:
        """removes tail, ie LRU element """
        if self.stack.len < 1:
            return None
        removed = self.stack.tail
        self.stack.remove(removed)
        assert removed.value in self.dic
        del self.dic[removed.value]
        return removed.value

    def __purge__(self) -> [int, int]:
        """
        clean ratio must be between 0 and 1,
        defaults to .25 or one-fourth
        """
        init_len = self.len
        target = self.size * self.purge_ratio
        while target > 0 and self.stack.len > 0:
            _removed = self.__pop__()
            target -= 1
        final_len = self.len
        return init_len, final_len

    def get(self, key: str) -> Optional[T]:
        if self.len < 1:
            return None
        if key not in self.dic:
            return None
        item = self.dic[key]
        if item is None:
            return None
        self.stack.remove(item.node)
        item.node = self.stack.push_head(item.value)
        return item.value

    def put(self, key: str, value: T) -> None:
        """pushing one too many elements triggers purge"""
        if not self.__have_vacancy__():
            change = self.__purge__()
            print(f"purged from {change[0]} to {change[1]}")

        if key in self.dic:
            item: LRUItem = self.dic[key]
            self.stack.remove(item.node)
            item.node = self.stack.push_head(value)
        else:
            head = self.stack.push_head(key)
            self.dic[key] = LRUItem(key=key, value=value, node=head)