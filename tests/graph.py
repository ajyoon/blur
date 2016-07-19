import unittest
from blur.markov import graph, nodes


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.test_graph = graph.Graph()
        self.node_1 = nodes.Node('Node 1')
        self.node_2 = nodes.Node('Node 2')
        self.node_3 = nodes.Node('Node 3')
        self.test_graph.node_list.extend([
            self.node_1,
            self.node_2,
            self.node_3])
        self.node_1.link_list.append(nodes.Link(self.node_2, 234))
        self.node_1.link_list.append(nodes.Link(self.node_3, 375))
        self.node_2.link_list.append(nodes.Link(self.node_1, 124))
        self.node_2.link_list.append(nodes.Link(self.node_3, 247))
        self.node_3.link_list.append(nodes.Link(self.node_1, 123))
        self.node_3.link_list.append(nodes.Link(self.node_2, 234))

    def test_init_with_existing_list_of_nodes(self):
        other_test_graph = graph.Graph([self.node_1,
                                        self.node_2,
                                        self.node_3])
        self.assertTrue(self.node_1 in other_test_graph.node_list)
        self.assertTrue(self.node_2 in other_test_graph.node_list)
        self.assertTrue(self.node_3 in other_test_graph.node_list)

    def test_merge_nodes(self):
        self.test_graph.merge_nodes(self.node_1, self.node_2)
        self.assertEqual([(l.target, l.weight) for l in self.node_1.link_list],
                         [(self.node_3, 375 + 247), (self.node_1, 124)])

    def test_add_nodes_with_one_node(self):
        self.test_graph.add_nodes(nodes.Node('Node 4'))
        self.assertEqual(len(self.test_graph.node_list), 4)

    def test_add_nodes_with_multiple_nodes(self):
        self.test_graph.add_nodes([nodes.Node('Node 4'),
                                   nodes.Node('Node 5')])
        self.assertEqual(len(self.test_graph.node_list), 5)

    def test_add_nodes_with_merge_existing_names(self):
        self.test_graph.add_nodes(nodes.Node('Node 3'),
                                  merge_existing_names=True)
        self.assertEqual(len(self.test_graph.node_list), 3)

    def test_feather_links_allowing_self_links(self):
        self.test_graph.feather_links(1, include_self=True)
        # Python floating point rounding causes strange weights
        self.assertEqual(
            [(l.target, l.weight) for l in self.node_1.link_list],
            [(self.node_2, 234.4),
             (self.node_3, 375.26),
             (self.node_1, 0.33999999999999997)])

    def test_feather_links_not_allowing_self_links(self):
        self.test_graph.feather_links(1, include_self=False)
        self.assertEqual(
            [(l.target, l.weight) for l in self.node_1.link_list],
            [(self.node_2, 234.4),
             (self.node_3, 375.26)])

    def test_apply_noise_with_uniform_amount(self):
        UNIFORM_NOISE_AMOUNT = 0.1
        original_node_1_link_weights = [
            l.weight for l in self.node_1.link_list]
        self.test_graph.apply_noise(uniform_amount=UNIFORM_NOISE_AMOUNT)
        new_link_weights = [l.weight for l in self.node_1.link_list]
        for index, weight in enumerate(new_link_weights):
            weight_difference = (abs(weight -
                                     original_node_1_link_weights[index]) /
                                 original_node_1_link_weights[index])
            self.assertLessEqual(weight_difference, UNIFORM_NOISE_AMOUNT)

    def test_apply_noise_with_weighted_amount(self):
        MAX_NOISE_WEIGHT = 0.1
        NOISE_WEIGHTS = [(0, 1), (MAX_NOISE_WEIGHT, 10)]
        original_node_1_link_weights = [
            l.weight for l in self.node_1.link_list]
        self.test_graph.apply_noise(noise_weights=NOISE_WEIGHTS)
        new_link_weights = [l.weight for l in self.node_1.link_list]
        for index, weight in enumerate(new_link_weights):
            weight_difference = (abs(weight -
                                     original_node_1_link_weights[index]) /
                                 original_node_1_link_weights[index])
            self.assertLessEqual(weight_difference, MAX_NOISE_WEIGHT)

    def test_find_node_by_name(self):
        found_node = self.test_graph.find_node_by_name('Node 2')
        self.assertEqual(found_node, self.node_2)

    def test_find_node_by_name_with_invalid_name(self):
        with self.assertRaises(ValueError):
            self.test_graph.find_node_by_name('bogus name')

    def test_remove_node(self):
        self.test_graph.remove_node(self.node_2)
        self.assertEqual(self.test_graph.node_list,
                         [self.node_1, self.node_3])
        self.assertEqual(len(self.test_graph.node_list[0].link_list), 1)
        self.assertEqual(len(self.test_graph.node_list[1].link_list), 1)

    def test_remove_node_by_name(self):
        self.test_graph.remove_node_by_name('Node 1')
        self.assertEqual(self.test_graph.node_list,
                         [self.node_2, self.node_3])
        # Test that no links point to any node named 'Node 1'
        for n in self.test_graph.node_list:
            self.assertFalse('Node 1' in [l.target.name for l in n.link_list])

    def test_remove_node_by_name_with_invalid_name(self):
        self.test_graph.remove_node_by_name('bogus name')
        self.assertEqual(self.test_graph.node_list,
                         [self.node_1, self.node_2, self.node_3])

    def test_has_node_with_name(self):
        self.assertTrue(self.test_graph.has_node_with_name('Node 1'))
        self.assertFalse(self.test_graph.has_node_with_name('bogus name'))

    def test_pick_with_no_starting_or_current_node(self):
        # Pick with starting_node=None and
        # self.test_graph.current_node=None, should pick a random node
        picked_node = self.test_graph.pick(starting_node=None)
        self.assertTrue(picked_node in self.test_graph.node_list)
        # Test that self.test_graph.current_node correctly updated
        self.assertEqual(self.test_graph.current_node, picked_node)

    def test_pick_with_no_starting_node_but_with_current_node(self):
        # Pick with starting_node=None, but with a
        # valid self.test_graph.current_node
        self.test_graph.current_node = self.node_1
        picked_node = self.test_graph.pick(starting_node=None)
        self.assertTrue(picked_node in [self.node_2, self.node_3])
        # Test that self.test_graph.current_node correctly updated
        self.assertEqual(self.test_graph.current_node, picked_node)

    def test_pick_with_starting_node(self):
        # Pick with a starting_node
        picked_node = self.test_graph.pick(starting_node=self.node_1)
        self.assertTrue(picked_node in [self.node_2, self.node_3])
        # Test that self.test_graph.current_node correctly updated
        self.assertEqual(self.test_graph.current_node, picked_node)
