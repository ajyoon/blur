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

    def test_init(self):
        # TODO: Build me!
        pass

    def test_find_link(self):
        # TODO: Build me!
        pass

    def test_add_link(self):
        # TODO: Build me!
        pass

    def test_add_link_to_self(self):
        # TODO: Build me!
        pass

    def test_add_reciprocal_link(self):
        # TODO: Build me!
        pass

    def test_remove_links_to_self(self):
        # TODO: Build me!
        pass

    def test_get_value(self):
        # TODO: Build me!
        pass
