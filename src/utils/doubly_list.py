"""Implementation of a doubly linked list"""
#from dataclasses import dataclass, field
from typing import Any, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")

class Node(BaseModel):
    """Doubly-linked node"""
    value: T
    next: Optional["Node"] = None
    prev: Optional["Node"] = None


class DLL(BaseModel):
    """Doubly-linked list"""
    head: Optional[Node] = None
    tail: Optional[Node] = None
    len: int = 0
    size: int = 0 # 0 for unlimited


    def __is_first__(self):
        return self.len == 0


    def __add_first__(self, new: Node) -> None:
        new.next = None
        new.prev = None
        self.head = new
        self.tail = new
        self.len = 1


    def push_head(self, node: Node) -> None:
        if self.__is_first__():
            return self.__add_first__(node)

        tmp = self.head
        tmp.prev = node
        node.next = tmp
        node.prev = None
        self.head = node
        self.len += 1


    def push_tail(self, new: Node) -> None:
        if self.__is_first__():
            return self.__add_first__(new)

        tmp = self.head
        tmp.prev = new
        new.next = tmp
        new.prev = None
        self.head = new
        self.len += 1


    def remove(self, node: Node) -> None:
        nex: Optional[Node] = node.next
        prev: Optional[Node] = node.prev
        if prev is not None and nex is not None:
            # removing middle
            nex.prev = prev
            prev.next = nex
        elif prev is not None:
            # removing tail
            prev.next = None
            self.tail = prev
        elif nex is not None:
            # removing head
            nex.prev = None
            self.head = nex
        else:
            # removing last element
            self.head = None
            self.tail = None

        self.len -= 1