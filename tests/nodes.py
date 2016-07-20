import unittest

from blur.markov import nodes


class Link(unittest.TestCase):
    def test_init(self):
        node = nodes.Node('Test Node')
        link = nodes.Link(node, 1)
        self.assertEqual(link.target, node)
        self.assertEqual(link.weight, 1)


class Node(unittest.TestCase):
    def setUp(self):
        self.main_node = nodes.Node('Main Test Node')
        self.other_node = nodes.Node('Other Test Node')
        self.main_link = nodes.Link(self.other_node, 1)
        self.other_link = nodes.Link(self.main_node, 1)
        self.main_node.link_list.append(self.main_link)
        self.other_node.link_list.append(self.other_link)

    def test_init(self):
        # since setUp() already calls init, just verify that it worked
        self.assertEqual(self.main_node.name, 'Main Test Node')
        self.assertFalse(self.main_node.self_destruct)
        self.assertEqual(self.main_node.link_list, [self.main_link])

    def test_merge_links_from(self):
        extra_test_link = nodes.Link(self.other_node, 5)
        self.other_node.link_list.append(extra_test_link)

        self.main_node.merge_links_from(self.other_node)
        # Test that only one link was added to self.main_node
        self.assertEqual(len(self.main_node.link_list), 2)
        # Test that the weight of extra_test_link was added to self.main_link
        self.assertEqual(self.main_node.link_list[0], self.main_link)
        self.assertEqual(self.main_link.weight, 6)
        # Test that the added link is a new link, not the old link
        self.assertNotEqual(self.main_node.link_list[1], self.other_link)
        self.assertEqual(self.main_node.link_list[1].target, self.main_node)
        self.assertEqual(self.main_node.link_list[1].weight, 1)

    def test_merge_links_from_with_merge_same_name_targets(self):
        new_node_with_existing_name = nodes.Node('Other Test Node')
        extra_test_link = nodes.Link(new_node_with_existing_name, 5)
        self.other_node.link_list.append(extra_test_link)

        self.main_node.merge_links_from(self.other_node,
                                        merge_same_name_targets=True)
        # Test that only one link was added to self.main_node
        self.assertEqual(len(self.main_node.link_list), 2)
        # Test that the weight of extra_test_link was added to self.main_link
        self.assertEqual(self.main_node.link_list[0], self.main_link)
        self.assertEqual(self.main_link.weight, 6)
        # Test that the added link is a new link, not the old link
        self.assertNotEqual(self.main_node.link_list[1], self.other_link)
        self.assertEqual(self.main_node.link_list[1].target, self.main_node)
        self.assertEqual(self.main_node.link_list[1].weight, 1)

    def test_find_link(self):
        found_link = self.main_node.find_link(self.other_node)
        self.assertEqual(found_link, self.main_link)
        # Test target value not found should return None
        unlinked_to_node = nodes.Node("Node that isn't linked to")
        bad_found_link = self.main_node.find_link(unlinked_to_node)
        self.assertIsNone(bad_found_link)

    def test_add_link_with_one_target(self):
        additional_node = nodes.Node('Additional Node')
        LINK_WEIGHT = 10
        self.main_node.add_link(additional_node, weight=LINK_WEIGHT)
        # Check that the link was added and has the correct weight
        new_link = self.main_node.link_list[-1]
        self.assertEqual(new_link.target, additional_node)
        self.assertEqual(new_link.weight, LINK_WEIGHT)

    def test_add_link_with_multiple_targets(self):
        additional_node_1 = nodes.Node('Additional Node 1')
        additional_node_2 = nodes.Node('Additional Node 2')
        LINK_WEIGHT = 10
        self.main_node.add_link([additional_node_1, additional_node_2],
                                weight=LINK_WEIGHT)
        # Check that the links were added and have the correct weight
        new_link_1 = self.main_node.link_list[-2]
        self.assertEqual(new_link_1.target, additional_node_1)
        self.assertEqual(new_link_1.weight, LINK_WEIGHT)
        new_link_2 = self.main_node.link_list[-1]
        self.assertEqual(new_link_2.target, additional_node_2)
        self.assertEqual(new_link_2.weight, LINK_WEIGHT)

    def test_add_link_to_existing_node(self):
        ADDED_LINK_WEIGHT = 10
        original_link_weight = self.main_link.weight
        original_link_list_length = len(self.main_node.link_list)
        self.main_node.add_link(self.other_node, weight=ADDED_LINK_WEIGHT)
        # Check that main_node.link_list did not gain a link
        self.assertEqual(len(self.main_node.link_list),
                         original_link_list_length)
        # Check that ADDED_LINK_WEIGHT was added to self.main_link.weight
        self.assertEqual(self.main_link.weight,
                         original_link_weight + ADDED_LINK_WEIGHT)

    def test_add_link_to_self_with_one_source(self):
        LINK_WEIGHT = 1
        additional_node = nodes.Node('Additional Node')
        self.main_node.add_link_to_self(additional_node, LINK_WEIGHT)
        # Check that the link was added and has the correct weight
        new_link = additional_node.link_list[-1]
        self.assertEqual(new_link.target, self.main_node)
        self.assertEqual(new_link.weight, LINK_WEIGHT)

    def test_add_link_to_self_with_multiple_sources(self):
        LINK_WEIGHT = 1
        additional_node_1 = nodes.Node('Additional Node 1')
        additional_node_2 = nodes.Node('Additional Node 2')
        self.main_node.add_link_to_self([additional_node_1, additional_node_2],
                                        LINK_WEIGHT)
        # Check that the link was added and has the correct weight
        new_link_1 = additional_node_1.link_list[-1]
        self.assertEqual(new_link_1.target, self.main_node)
        self.assertEqual(new_link_1.weight, LINK_WEIGHT)
        new_link_2 = additional_node_2.link_list[-1]
        self.assertEqual(new_link_2.target, self.main_node)
        self.assertEqual(new_link_2.weight, LINK_WEIGHT)

    def test_add_reciprocal_link_with_one_target(self):
        LINK_WEIGHT = 1
        additional_node = nodes.Node('Additional Node')
        self.main_node.add_reciprocal_link(additional_node, LINK_WEIGHT)
        # Test that both links were added
        new_link_1 = self.main_node.link_list[-1]
        self.assertEqual(new_link_1.target, additional_node)
        self.assertEqual(new_link_1.weight, LINK_WEIGHT)
        new_link_2 = additional_node.link_list[-1]
        self.assertEqual(new_link_2.target, self.main_node)
        self.assertEqual(new_link_2.weight, LINK_WEIGHT)

    def test_add_reciprocal_link_with_multiple_targets(self):
        LINK_WEIGHT = 1
        additional_node_1 = nodes.Node('Additional Node 1')
        additional_node_2 = nodes.Node('Additional Node 2')
        self.main_node.add_reciprocal_link(
            [additional_node_1, additional_node_2],
            LINK_WEIGHT)
        # Test that all links were added as expected
        # Test links in self.main_node
        new_link_1 = self.main_node.link_list[-2]
        self.assertEqual(new_link_1.target, additional_node_1)
        self.assertEqual(new_link_1.weight, LINK_WEIGHT)
        new_link_2 = self.main_node.link_list[-1]
        self.assertEqual(new_link_2.target, additional_node_2)
        self.assertEqual(new_link_2.weight, LINK_WEIGHT)
        # Test links in additional_node_1
        new_link_3 = additional_node_1.link_list[-1]
        self.assertEqual(new_link_3.target, self.main_node)
        self.assertEqual(new_link_3.weight, LINK_WEIGHT)
        # Test links in additional_node_2
        new_link_4 = additional_node_2.link_list[-1]
        self.assertEqual(new_link_4.target, self.main_node)
        self.assertEqual(new_link_4.weight, LINK_WEIGHT)

    def test_remove_links_to_self(self):
        # Manually add a link pointing from self.main_node to itself
        new_link = nodes.Link(self.main_node, 1)
        self.main_node.link_list.append(new_link)
        self.main_node.remove_links_to_self()
        self.assertFalse(self.main_node in
                         [l.target for l in self.main_node.link_list])

    def test_get_value(self):
        value = self.main_node.get_value()
        self.assertEqual(value, self.main_node.name)
