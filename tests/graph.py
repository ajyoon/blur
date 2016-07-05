import unittest
from ..markov import graph, nodes


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

    def test_merge_nodes(self):
        self.test_graph.merge_nodes(self.node_1, self.node_2)
        # sort the two comparison lists somehow so they line up correctly
        print([(l.target.name, l.weight) for l in self.node_1.link_list])
        self.assertEqual([(l.target, l.weight) for l in self.node_1.link_list],
                         [(self.node_3, 375 + 247), (self.node_1, 124)])

    def test_add_nodes_with_one_node(self):
        self.test_graph.add_nodes(nodes.Node('Node 4'))
        self.assertEqual(len(self.test_graph.node_list), 4)

    def test_add_nodes_with_multiple_nodes(self):
        self.test_graph.add_nodes([nodes.Node('Node 4'),
                                   nodes.Node('Node 5')])
        self.assertEqual(len(self.test_graph.node_list), 5)

    def test_feather_links(self):
        # Todo: Build me
        pass

    def test_apply_noise(self):
        # Todo: Build me
        pass

    def test_find_node_by_name(self):
        found_node = self.test_graph.find_node_by_name('Node 2')
        self.assertEqual(found_node, self.node_2)

    def test_remove_node(self):
        self.test_graph.remove_node(self.node_2)
        self.assertEqual(self.test_graph.node_list,
                         [self.node_1, self.node_3])
        self.assertEqual(len(self.test_graph.node_list[0].link_list), 1)
        self.assertEqual(len(self.test_graph.node_list[1].link_list), 1)

    def test_remove_node_by_name(self):
        # Todo: Build me
        pass

    def test_has_node_with_name(self):
        self.assertTrue(self.test_graph.has_node_with_name('Node 1'))
        self.assertFalse(self.test_graph.has_node_with_name('bogus name'))

    def test_pick_by_use_weight(self):
        # Todo: Build me
        pass

    def test_pick(self):
        # Todo: Build me
        pass

    def test_walk(self):
        # Todo: Build me
        pass
