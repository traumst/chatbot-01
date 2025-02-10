from unittest import main, TestCase
from doubly_list import DLL, Node

class TestDoublyList(TestCase):

    def test_create(self):
        list1 = DLL(size=128)
        self.assertEqual(0, list1.len)

    def test_push_head(self):
        list1 = DLL(size=128)
        node = Node(value=1)
        list1.push_head(node)
        self.assertEqual(1, list1.len)

    def test_push_tail(self):
        list1 = DLL(size=128)
        node = Node(value=1)
        list1.push_head(node)
        self.assertEqual(1, list1.len)

    def test_remove(self):
        list1 = DLL(size=128)
        nodes = [Node(value=1), Node(value=2), Node(value=3), Node(value=4)]
        for node in nodes:
            list1.push_head(node)

        self.assertEqual(4, list1.len)
        list1.remove(nodes[1])
        self.assertEqual(3, list1.len)

if __name__ == '__main__':
    main()