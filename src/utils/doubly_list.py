"""Implementation of a doubly linked list"""
import os
from typing import Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar(name="T")

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
    # use size 0 for unlimited
    size: int


    def __is_first__(self):
        return self.len == 0


    def __add_first__(self, value: T) -> Node:
        node = Node(value=value)
        node.next = None
        node.prev = None
        self.head = node
        self.tail = node
        self.len = 1
        return node


    def length(self) -> int:
        return self.len


    def push_head(self, value: T) -> Node:
        if self.__is_first__():
            return self.__add_first__(value)

        node = Node(value=value)
        top = self.head
        top.prev = node
        node.next = top
        node.prev = None
        self.head = node
        self.len += 1
        return node


    def push_tail(self, value: T) -> Node:
        if self.__is_first__():
            return self.__add_first__(value)

        node = Node(value=value)
        btm = self.tail
        btm.next = node
        node.prev = btm
        node.next = None
        self.tail = node
        self.len += 1
        return node


    def remove(self, node: Node) -> None:
        if ((node.prev is None or node.next is None)
                and self.head.value != node.value
                and self.tail.value != node.value):
            return

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

        node.next = None
        node.prev = None
        self.len -= 1