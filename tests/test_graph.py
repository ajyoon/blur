import unittest

from blur.markov.graph import Graph
from blur.markov.node import Node, Link


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.test_graph = Graph()
        self.node_1 = Node('Node 1')
        self.node_2 = Node('Node 2')
        self.node_3 = Node('Node 3')
        self.test_graph.node_list.extend([
            self.node_1,
            self.node_2,
            self.node_3])
        self.node_1.link_list.append(Link(self.node_2, 234))
        self.node_1.link_list.append(Link(self.node_3, 375))
        self.node_2.link_list.append(Link(self.node_1, 124))
        self.node_2.link_list.append(Link(self.node_3, 247))
        self.node_3.link_list.append(Link(self.node_1, 123))
        self.node_3.link_list.append(Link(self.node_2, 234))

    def test_init_with_existing_list_of_nodes(self):
        other_test_graph = Graph([self.node_1,
                                  self.node_2,
                                  self.node_3])
        self.assertTrue(self.node_1 in other_test_graph.node_list)
        self.assertTrue(self.node_2 in other_test_graph.node_list)
        self.assertTrue(self.node_3 in other_test_graph.node_list)

    def test_str(self):
        expected = """graph.Graph instance with 3 nodes:
    0: Node 1
    1: Node 2
    2: Node 3"""
        self.assertMultiLineEqual(expected, self.test_graph.__str__())

    def test_merge_nodes(self):
        self.test_graph.merge_nodes(self.node_1, self.node_2)
        self.assertEqual([(l.target, l.weight) for l in self.node_1.link_list],
                         [(self.node_3, 375 + 247), (self.node_1, 124 + 234)])
        self.assertEqual([(l.target, l.weight) for l in self.node_3.link_list],
                         [(self.node_1, 123 + 234)])

    # def test_merge_nodes_with_graph_links_pointing_to_kill_node(self):
    #     self.test_graph.merge_nodes(self.node_1, self.node_2)

    def test_add_nodes_with_one_node(self):
        self.test_graph.add_nodes(Node('Node 4'))
        self.assertEqual(len(self.test_graph.node_list), 4)

    def test_add_nodes_with_multiple_nodes(self):
        self.test_graph.add_nodes([Node('Node 4'),
                                   Node('Node 5')])
        self.assertEqual(len(self.test_graph.node_list), 5)

    def test_feather_links_allowing_self_links(self):
        self.test_graph.feather_links(1, include_self=True)
        self.assertEqual(self.node_1.link_list[0].target, self.node_2)
        self.assertAlmostEqual(self.node_1.link_list[0].weight, 234.4)
        self.assertEqual(self.node_1.link_list[1].target, self.node_3)
        self.assertAlmostEqual(self.node_1.link_list[1].weight, 375.26)
        self.assertEqual(self.node_1.link_list[2].target, self.node_1)
        self.assertAlmostEqual(self.node_1.link_list[2].weight, 0.34)

    def test_feather_links_not_allowing_self_links(self):
        self.test_graph.feather_links(1, include_self=False)
        self.assertEqual(self.node_1.link_list[0].target, self.node_2)
        self.assertAlmostEqual(self.node_1.link_list[0].weight, 234.4)
        self.assertEqual(self.node_1.link_list[1].target, self.node_3)
        self.assertAlmostEqual(self.node_1.link_list[1].weight, 375.26)

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

    def test_find_node_by_value(self):
        found_node = self.test_graph.find_node_by_value('Node 2')
        self.assertEqual(found_node, self.node_2)

    def test_find_node_by_value_with_invalid_value(self):
        self.assertIsNone(self.test_graph.find_node_by_value('bogus value'))

    def test_remove_node(self):
        self.test_graph.remove_node(self.node_2)
        self.assertEqual(self.test_graph.node_list,
                         [self.node_1, self.node_3])
        self.assertEqual(len(self.test_graph.node_list[0].link_list), 1)
        self.assertEqual(len(self.test_graph.node_list[1].link_list), 1)

    def test_remove_node_with_node_not_in_graph_does_nothing(self):
        node_not_in_graph = Node('Node not in the graph')
        self.test_graph.remove_node(node_not_in_graph)
        self.assertEqual(self.test_graph.node_list,
                         [self.node_1, self.node_2, self.node_3])

    def test_remove_node_by_value(self):
        self.test_graph.remove_node_by_value('Node 1')
        self.assertEqual(self.test_graph.node_list,
                         [self.node_2, self.node_3])
        # Test that no links point to any node valued 'Node 1'
        for n in self.test_graph.node_list:
            self.assertFalse('Node 1' in [l.target.value for l in n.link_list])

    def test_remove_node_by_value_with_invalid_value(self):
        self.test_graph.remove_node_by_value('bogus value')
        self.assertEqual(self.test_graph.node_list,
                         [self.node_1, self.node_2, self.node_3])

    def test_has_node_with_value(self):
        self.assertTrue(self.test_graph.has_node_with_value('Node 1'))
        self.assertFalse(self.test_graph.has_node_with_value('bogus value'))

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

    def test_from_string_with_defaults(self):
        source = ('I have <<nothing to say,.;!?:\\/\'"()[>>'
                  'and I am saying it and that is poetry.')
        # Defaults:
        # distance_weights = {1: 1}
        # merge_same_words = False
        built_graph = Graph.from_string(source)
        # Should result in a graph with one node per word in the source string,
        # each with exactly one link pointing to the following word
        # (last word wrapping to the first)
        self.assertEqual(len(built_graph.node_list), 13)
        for n in built_graph.node_list:
            self.assertEqual(len(n.link_list), 1)
            self.assertEqual(n.link_list[0].weight, 1)
        # Test the specifics of the graph
        # Value of the node
        # and value of the node it is linked to
        self.assertEqual(built_graph.node_list[0].value, 'I')
        self.assertEqual(built_graph.node_list[0].link_list[0].target.value,
                         'have')
        # etc...
        self.assertEqual(built_graph.node_list[1].value, 'have')
        self.assertEqual(built_graph.node_list[1].link_list[0].target.value,
                         'nothing to say,.;!?:\\/\'"()[')
        self.assertEqual(built_graph.node_list[2].value,
                         'nothing to say,.;!?:\\/\'"()[')
        self.assertEqual(built_graph.node_list[2].link_list[0].target.value,
                         'and')
        self.assertEqual(built_graph.node_list[3].value, 'and')
        self.assertEqual(built_graph.node_list[3].link_list[0].target.value,
                         'I')
        self.assertEqual(built_graph.node_list[4].value, 'I')
        self.assertEqual(built_graph.node_list[4].link_list[0].target.value,
                         'am')
        self.assertEqual(built_graph.node_list[5].value, 'am')
        self.assertEqual(built_graph.node_list[5].link_list[0].target.value,
                         'saying')
        self.assertEqual(built_graph.node_list[6].value, 'saying')
        self.assertEqual(built_graph.node_list[6].link_list[0].target.value,
                         'it')
        self.assertEqual(built_graph.node_list[7].value, 'it')
        self.assertEqual(built_graph.node_list[7].link_list[0].target.value,
                         'and')
        self.assertEqual(built_graph.node_list[8].value, 'and')
        self.assertEqual(built_graph.node_list[8].link_list[0].target.value,
                         'that')
        self.assertEqual(built_graph.node_list[9].value, 'that')
        self.assertEqual(built_graph.node_list[9].link_list[0].target.value,
                         'is')
        self.assertEqual(built_graph.node_list[10].value, 'is')
        self.assertEqual(built_graph.node_list[10].link_list[0].target.value,
                         'poetry')
        self.assertEqual(built_graph.node_list[11].value, 'poetry')
        self.assertEqual(built_graph.node_list[11].link_list[0].target.value,
                         '.')
        self.assertEqual(built_graph.node_list[12].value, '.')
        # Wraps around to first word
        self.assertEqual(built_graph.node_list[12].link_list[0].target.value,
                         'I')

    def test_from_string_with_default_weights_and_merge_same_words(self):
        source = ('I have <<nothing to say,.;!?:\\/\'"()[>>'
                  'and I am saying it and that is poetry.')
        # Default distance_weights = {1: 1}
        built_graph = Graph.from_string(source, merge_same_words=True)
        # Should result in a graph with one node per word in the source string,
        # each with exactly one link pointing to the following word
        # (last word wrapping to the first)
        self.assertEqual(len(built_graph.node_list), 11)
        # Test that no two nodes have the same value
        for index, node in enumerate(built_graph.node_list):
            for other_index, other_node in enumerate(built_graph.node_list):
                if other_index == index:
                    continue
                self.assertTrue(other_node.value != node.value)
        # Node for 'I' should have two links, one pointing to 'have' and
        # one pointing to 'am'
        self.assertEqual(len(built_graph.node_list[0].link_list), 2)
        self.assertEqual(built_graph.node_list[0].link_list[0].target.value,
                         'have')
        self.assertEqual(built_graph.node_list[0].link_list[1].target.value,
                         'am')

    def test_from_string_with_custom_weights_and_merging_same_words(self):
        source = ('I have <<nothing to say,.;!?:\\/\'"()[>>'
                  'and I am saying it and that is poetry.')
        weights = {-5: 1, 0: 2, 1: 3, 4: 5}
        built_graph = Graph.from_string(source,
                                        distance_weights=weights,
                                        merge_same_words=True)
        # Should result in a graph with one node per word in the source string,
        # each with exactly one link pointing to the following word
        # (last word wrapping to the first)
        self.assertEqual(len(built_graph.node_list), 11)
        # Test that no two nodes have the same value
        for index, node in enumerate(built_graph.node_list):
            for other_index, other_node in enumerate(built_graph.node_list):
                if other_index == index:
                    continue
                self.assertTrue(other_node.value != node.value)

        # Test the order in which nodes were added is as expected
        self.assertEqual(built_graph.node_list[0].value,  'I')
        self.assertEqual(built_graph.node_list[1].value,  'have')
        self.assertEqual(built_graph.node_list[2].value,
                         'nothing to say,.;!?:\\/\'"()[')
        self.assertEqual(built_graph.node_list[3].value,  'and')
        self.assertEqual(built_graph.node_list[4].value,  'am')
        self.assertEqual(built_graph.node_list[5].value,  'saying')
        self.assertEqual(built_graph.node_list[6].value,  'it')
        self.assertEqual(built_graph.node_list[7].value,  'that')
        self.assertEqual(built_graph.node_list[8].value,  'is')
        self.assertEqual(built_graph.node_list[9].value,  'poetry')
        self.assertEqual(built_graph.node_list[10].value, '.')

        # Exhaustively test the node with the value 'I'
        # Find the node with the value 'I' (do this manually)
        i_node = next(n for n in built_graph.node_list if n.value == 'I')
        # Compare link contents of 'I' against expected values
        self.assertEqual(len(i_node.link_list), 5)
        self.assertEqual(i_node.link_list[0].target.value, 'and')
        self.assertEqual(i_node.link_list[0].weight, 1 + 5)
        self.assertEqual(i_node.link_list[1].target.value, 'I')
        self.assertEqual(i_node.link_list[1].weight, 2 + 5 + 2)
        self.assertEqual(i_node.link_list[2].target.value, 'have')
        self.assertEqual(i_node.link_list[2].weight, 3)
        self.assertEqual(i_node.link_list[3].target.value, '.')
        self.assertEqual(i_node.link_list[3].weight, 1)
        self.assertEqual(i_node.link_list[4].target.value, 'am')
        self.assertEqual(i_node.link_list[4].weight, 3)

    def test_from_string_with_punc_inside_word(self):
        source = ("I'm a human!")
        built_graph = Graph.from_string(source)
        self.assertEqual(len(built_graph.node_list), 4)
        self.assertEqual(built_graph.node_list[0].value,  "I'm")
        self.assertEqual(built_graph.node_list[1].value,  'a')
        self.assertEqual(built_graph.node_list[2].value,  'human')
        self.assertEqual(built_graph.node_list[3].value,  '!')

    def test_from_file_is_same_as_from_string_of_file_contents(self):
        # Defaults:
        # distance_weights = {1: 1}
        # merge_same_words = False
        # test_source_text contents are the exact same as "source_as_string",
        # but with Python escape characters removed
        try:
            file_name = 'tests/test_source_text.txt'
        except FileNotFoundError:
            # Maybe we're testing from within the tests folder...
            file_name = 'test_source_text.txt'
        graph_from_file = Graph.from_file(file_name)

        source_as_string = ('I have <<nothing to say,.;!?:\\/\'"()[>>'
                            'and I am saying it and that is poetry.')
        graph_from_string = Graph.from_string(source_as_string)
        for file_node, string_node in zip(graph_from_file.node_list,
                                          graph_from_string.node_list):
            self.assertEqual(file_node.value, string_node.value)
            for file_link, string_link in zip(file_node.link_list,
                                              string_node.link_list):
                self.assertEqual(file_link.target.value,
                                 string_link.target.value)
                self.assertEqual(file_link.weight, string_link.weight)

    def test_from_string_with_default_group_marker(self):
        source = ('I have <<nothing to say,.;!?:\\/\'"()[>>'
                  'and I am saying it and that is poetry.')
        built_graph = Graph.from_string(source)
        self.assertEqual(built_graph.node_list[2].value,
                         'nothing to say,.;!?:\\/\'"()[')

    def test_from_string_with_custom_group_marker(self):
        source = ('I have {nothing to say,.;!?:\\/\'"()[}'
                  'and I am saying it and that is poetry.')
        built_graph = Graph.from_string(source,
                                        group_marker_opening='{',
                                        group_marker_closing='}')
        self.assertEqual(built_graph.node_list[2].value,
                         'nothing to say,.;!?:\\/\'"()[')

    def test_from_file_with_custom_group_marker(self):
        try:
            file_name = 'tests/test_source_text_2.txt'
        except FileNotFoundError:
            # Maybe we're testing from within the tests folder...
            file_name = 'test_source_text_2.txt'
        graph_from_file = Graph.from_file(file_name,
                                          group_marker_opening='{',
                                          group_marker_closing='}')
        self.assertEqual(graph_from_file.node_list[2].value,
                         'nothing to say,.;!?:\\/\'"()[')
