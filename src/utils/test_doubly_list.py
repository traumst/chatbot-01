from unittest import main, TestCase
from src.utils.doubly_list import DLL, Node

class TestDoublyList(TestCase):

    def test_create(self):
        list1 = DLL(size=128)
        self.assertEqual(0, list1.len)

    def test_push_head(self):
        list1 = DLL(size=128)
        node = list1.push_head(value=111)
        self.assertNotEqual(None, node)
        self.assertEqual(111, node.value)
        self.assertEqual(1, list1.len)

    def test_push_tail(self):
        list1 = DLL(size=128)
        node = list1.push_head(111)
        self.assertNotEqual(None, node)
        self.assertEqual(111, node.value)
        self.assertEqual(1, list1.len)

    def test_remove(self):
        list1: DLL = DLL(size=128)
        created: [Node] = [list1.push_head((n+1) * 111) for n in range(4)]
        self.assertEqual(4, list1.len)
        self.assertEqual(4, len(created))
        list1.remove(created[1])
        list1.remove(created[2])
        list1.remove(created[0])
        self.assertEqual(1, list1.len)
        self.assertEqual(444, list1.head.value)
        self.assertEqual(444, list1.tail.value)

    def test_remove_str(self):
        list1: DLL = DLL(size=128)
        created: [Node] = [list1.push_head((n + 1) * "hey ") for n in range(4)]
        self.assertEqual(4, list1.len)
        self.assertEqual(4, len(created))
        list1.remove(created[2])
        list1.remove(created[0])
        list1.remove(created[3])
        self.assertEqual(1, list1.len)
        self.assertEqual("hey hey ", list1.head.value)
        self.assertEqual("hey hey ", list1.tail.value)

    def test_remove_missing(self):
        list1: DLL = DLL(size=128)
        created: [Node] = [list1.push_head((n + 1) * 111) for n in range(4)]
        list1.remove(created[1])
        list1.remove(created[1])
        self.assertEqual(3, list1.len)

if __name__ == '__main__':
    main()