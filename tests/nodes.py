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
        self.main_test_node = nodes.Node('Main Test Node')
        self.other_test_node = nodes.Node('Other Test Node')
        self.main_test_link = nodes.Link(self.other_test_node, 1)
        self.other_test_link = nodes.Link(self.main_test_node, 1)
        self.main_test_node.link_list.append(self.main_test_link)
        self.other_test_node.link_list.append(self.other_test_link)

    def test_init(self):
        # since setUp() already calls init, just verify that it worked
        self.assertEqual(self.main_test_node.name, 'Main Test Node')
        self.assertFalse(self.main_test_node.self_destruct)
        self.assertEqual(self.main_test_node.use_weight, 1)
        self.assertEqual(self.main_test_node.link_list, [self.main_test_link])

    def test_find_link(self):
        found_link = self.main_test_node.find_link(self.other_test_node)
        self.assertEqual(found_link, self.main_test_link)
        # Test target value not found should return False
        unlinked_to_node = nodes.Node("Node that isn't linked to")
        bad_found_link = self.main_test_node.find_link(unlinked_to_node)
        self.assertIsNone(bad_found_link)

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
