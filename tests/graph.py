import unittest
from ..markov import graph, nodes


class TestGraph(unittest.TestCase):
    def test_merge_nodes(self):
        test_graph = graph.Graph()
        node_1 = nodes.Node('Node 1')
        node_2 = nodes.Node('Node 2')
        node_3 = nodes.Node('Node 3')
        test_graph.node_list.extend([
            node_1,
            node_2,
            node_3
        ])
        node_1.link_list.append(nodes.Link(node_2, 234))
        node_1.link_list.append(nodes.Link(node_3, 375))
        node_2.link_list.append(nodes.Link(node_1, 124))
        node_2.link_list.append(nodes.Link(node_3, 247))
        node_3.link_list.append(nodes.Link(node_1, 123))
        node_3.link_list.append(nodes.Link(node_2, 234))
        
        test_graph.merge_nodes(node_1, node_2)
        # sort the two comparison lists somehow so they line up correctly
        print([(l.target.name, l.weight) for l in node_1.link_list])
        self.assertEqual([(l.target, l.weight) for l in node_1.link_list],
                         [(node_3, 375 + 247), (node_1, 124)])

    def test_remove_node(self):
        test_graph = graph.Graph()
        node_1 = nodes.Node('Node 1')
        node_2 = nodes.Node('Node 2')
        test_graph.node_list.extend([node_1, node_2])
        node_1.link_list.append(nodes.Link(node_2, 1))
        node_2.link_list.append(nodes.Link(node_1, 2))

        test_graph.remove_node(node_2)
        self.assertEqual(len(test_graph.node_list), 1)
        self.assertEqual(len(test_graph.node_list[0].link_list), 0)
