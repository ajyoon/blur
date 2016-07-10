import unittest

from ..markov import nodes


class Link(unittest.TestCase):
    def test_init(self):
        node = nodes.Node('Test Node')
        link = nodes.Link(node, 1)
        self.assertEqual(link.target, node)
        self.assertEqual(link.weight, 1)


class Node(unittest.TestCase):
    def setUp(self):
        # TODO: Build me!
        pass

    def test___init__(self, name=None, self_destruct=False):
        # TODO: Build me!
        pass

    def test_find_link(self, target_value):
        # TODO: Build me!
        pass

    def test_add_link(self, targets, weight=1):
        # TODO: Build me!
        pass

    def test_add_link_to_self(self, source, weight):
        # TODO: Build me!
        pass

    def test_add_reciprocal_link(self, target, weight):
        # TODO: Build me!
        pass

    def test_remove_links_to_self(self):
        # TODO: Build me!
        pass

    def test_get_value(self):
        # TODO: Build me!
        pass
