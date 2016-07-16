
"""
UNDER RECONSTRUCTION - APOLOGIES FOR THE MESS
"""

from __future__ import division
import random
import re

from blur.rand import weighted_choice, weighted_rand
from . import nodes


class Graph:
    def __init__(self):
        self.node_list = []
        self.source = None
        self.current_node = None
        self.weight = None

    def merge_nodes(self, keep_node, kill_node):
        """
        Takes two nodes and merges them together, merging their links by
        combining the two link lists and summing the weights of links which
        point to the same node.

        Args:
            keep_node (Node): node to be kept
            kill_node (Node): node to be deleted

        Returns: None
        """
        # Merge links from kill_node to keep_node
        for kill_link in kill_node.link_list:
            for i, existing_link in enumerate(keep_node.link_list):
                if kill_link.target == existing_link.target:
                    existing_link.weight += kill_link.weight
                    break
            else:
                keep_node.add_link(kill_link.target, kill_link.weight)
        # Remove kill_node from the graph
        self.remove_node(kill_node)

    def add_nodes(self, nodes, merge_existing_names=False):
        """
        Add a given node or list of nodes to self.node_list.
        If a node already exists in the network, merge them

        Args:
            node (Node or list[node]):

            Returns: None
        """
        # Generalize nodes to a list
        if not isinstance(nodes, list):
            add_list = [nodes]
        else:
            add_list = nodes
        if merge_existing_names:
            for add_node in add_list:
                for currently_existing_node in self.node_list:
                    if currently_existing_node.name == add_node.name:
                        self.merge_nodes(currently_existing_node, add_node)
                        break
        else:
            self.node_list.extend(add_list)

    def feather_links(self, factor=0.01, include_self=False):
        """
        Feather the links of connected nodes.

        Go through every node in the network and make it inherit the links
        of the other nodes it is connected to. Because the link weight sum
        for any given node can be very different within a graph, the weights
        of inherited links are made proportional to the sum weight of the
        parent nodes.

        Args:
            factor (float): multiplier of neighbor links
            include_self (bool): whether nodes can inherit links pointing
                to themselves

        Returns: None
        """
        def feather_node(node):
            node_weight_sum = sum(l.weight for l in node.link_list)
            # Iterate over a copy of the original link list since we will
            # need to refer to this while modifying node.link_list
            for original_link in node.link_list[:]:
                neighbor_node = original_link.target
                neighbor_weight = original_link.weight
                feather_weight = neighbor_weight / node_weight_sum
                neighbor_node_weight_sum = sum(l.weight for
                                               l in neighbor_node.link_list)
                # Iterate over the links belonging to the neighbor_node,
                # copying its links to ``node`` with proportional weights
                for neighbor_link in neighbor_node.link_list:
                    if (not include_self) and (neighbor_link.target == node):
                        continue
                    relative_link_weight = (neighbor_link.weight /
                                            neighbor_node_weight_sum)
                    feathered_link_weight = round((relative_link_weight *
                                                   feather_weight * factor), 2)
                    node.add_link(neighbor_link.target, feathered_link_weight)
        for n in self.node_list:
            feather_node(n)

    def apply_noise(self, noise_weights=None, uniform_amount=0.1):
        """
        Add noise to every link in the network.

        Can use either a ``uniform_amount`` or a ``noise_weight`` weight
        profile. If ``noise_weight`` is set, ``uniform_amount`` will be
        ignored.

        Args:
            noise_weights (Optional[(amount, weight)]): a list of weights
                describing the noise to be added to each link
            uniform_amount (float): the maximum amount of uniform noise
                to be applied if ``noise_weights`` is not set

        Returns: None
        """
        # Main node loop
        for node in self.node_list:
            for link in node.link_list:
                if noise_weights is not None:
                    noise_amount = round(weighted_rand(noise_weights), 3)
                else:
                    noise_amount = round(random.uniform(
                        0, link.weight * uniform_amount), 3)
                link.weight += noise_amount

    def find_node_by_name(self, name):
        """
        Find and return a node in self.node_list with the name ``name``

        If multiple nodes exist with the name ``name``,
        return the first one found.

        Returns: Node

        Raises: ValueError if no node with
        """
        for node in self.node_list:
            if node.name == name:
                return node
        else:
            raise ValueError('Could not find node by name ' + str(name))

    def remove_node(self, node):
        """
        Remove a node from the graph, removing all links pointing to it

        If ``node`` is not in the graph, do nothing.

        Args:
            node (Node): The node to be removed

        Returns: None
        """
        if node not in self.node_list:
            return
        self.node_list.remove(node)
        # Remove links pointing to the deleted node
        for n in self.node_list:
            n.link_list = [link for link in n.link_list if
                           link.target != node]

    def remove_node_by_name(self, name):
        """
        Delete all nodes in self.node_list with the name ``name``

        Args:
            name (Any):

        Returns: None
        """
        self.node_list = [node for node in self.node_list if node.name != name]
        # Remove links pointing to the deleted node
        for node in self.node_list:
            node.link_list = [link for link in node.link_list if
                              link.target.name != name]

    def has_node_with_name(self, name):
        """
        Whether any node in self.node_list has name of ``name``

        Args:
            name (str)

        Returns: Bool
        """
        for node in self.node_list:
            if node.name == name:
                return True
        else:
            return False

    def pick_by_use_weight(self):
        """
        Pick a node in the graph based on node ``use_weight`` values.

        Additionally, set ``self.current_node`` to the newly picked node.

        Returns: Node
        """
        node = weighted_choice([(n.name, n.use_weight)
                                     for n in self.node_list])
        self.current_node = self.find_node_by_name(node)
        return self.current_node

    def pick(self, starting_node=None):
        """
        Pick a node on the graph based on the links in a starting node

        Additionally, set ``self.current_node`` to the newly picked node.

        * if starting_node is specified, start from there
        * if starting_node is None, start from self.current_node
        * if starting_node is None and self.current_node is None,
          pick from the network's nodes' use weights

        Args:
            starting_node (Optional[Node]): Node to pick from.

        Returns: Node
        """
        if starting_node is None:
            if self.current_node is None:
                return self.pick_by_use_weight()
            else:
                starting_node = self.current_node
        # Use weighted_choice on start_node.link_list
        self.current_node = weighted_choice(
            [(link.target, link.weight) for link in starting_node.link_list])
        return self.current_node

    def print_nodes_and_links(self):
        """
        Print a list of every node and what its links are

        Returns: None
        """
        print('Graph object:')
        for node in self.node_list:
            print('Node: {0}\n'
                  'Links:\n'
                  '--------'.format(node.name))
            for link in node.link_list:
                print('    target: {0}, target name: {1}|| weight: {2}\n'
                      '    .....................................'.format(
                          link.target, link.target.name, link.weight))
        print('=========================================================')

    @classmethod
    def from_file(cls,
                  source,
                  distance_weights=None,
                  allow_self_links=True,
                  merge_same_words=False):
        """
        Read a string from a file and generate a Graph object based on it

        Words and punctuation marks are made into nodes.
        To use whitespace and punctuation marks within a word
        (e.g. to make ``'hello, world!'``) into a single node, surround the
        text in question with angle brackets ``'<hello, world!>'``.

        This is a convenience function for opening a file and passing its
        contents to Graph.from_string()

        Args:
            source (str): the string to derive the graph from
            distance_weights (dict): dict of relative indices corresponding
                with word weights. For example, if a dict entry is ``1: 1000``
                this means that every word is linked to the word which follows
                it with a weight of 1000. ``-4: 350`` would mean that every
                word is linked to the 4th word behind it with a weight of 350.
                A key of ``0`` refers to the weight words get
                pointing to themselves. Keys pointing beyond the edge of the
                word list will wrap around the list.
            allow_self_links (bool): if words can be linked to themselves
            merge_same_words (bool): if nodes which have the same value should
                be merged or not.

        Returns: Graph
        """
        source_string = open(source, 'r').read()
        return cls.from_string(source_string,
                               distance_weights,
                               allow_self_links,
                               merge_same_words)

    @classmethod
    def from_string(cls,
                    source,
                    distance_weights=None,
                    allow_self_links=True,
                    merge_same_words=False):
        """
        Read a string and generate a Graph object based on it

        Words and punctuation marks are made into nodes.
        To use whitespace and punctuation marks within a word
        (e.g. to make ``'hello, world!'``) into a single node, surround the
        text in question with angle brackets ``'<hello, world!>'``.

        Args:
            source (str): the string to derive the graph from
            distance_weights (dict): dict of relative indices corresponding
                with word weights. For example, if a dict entry is ``1: 1000``
                this means that every word is linked to the word which follows
                it with a weight of 1000. ``-4: 350`` would mean that every
                word is linked to the 4th word behind it with a weight of 350.
                A key of ``0`` refers to the weight words get
                pointing to themselves. Keys pointing beyond the edge of the
                word list will wrap around the list.
            allow_self_links (bool): if words can be linked to themselves
            merge_same_words (bool): if nodes which have the same value should
                be merged or not.

        Returns: Graph
        """
        if distance_weights is None:
            distance_weights = {1: 1000, 2: 100, 3: 80, 4: 60, 5: 50,
                                6: 40, 7: 30, 8: 17, 9: 14, 10: 10,
                                11: 10, 12: 10, 13: 5, 14: 5, 15: 75}
        graph = cls()
        # regex that matches:
        #   * Anything surrounded by angle bracks,
        #   * The punctuation marks: , . ; ! ? : \ / ' " ( ) [ ]
        #   * Any continuous group of alphanumerical characters
        expression = '<(.+)>|([,\.\;\!\?\:\\\/\'\"\(\)\[\])|([a-zA-z0-9]+)'
        matches = re.findall(expression, source)
        # Un-tuple matches since we are only using groups to strip brackets
        # Is there a better way to do this?
        words = [next(t for t in match if t) for match in matches]
        temp_node_list = [nodes.Node(w) for w in words]

        for i, node in enumerate(temp_node_list):
            for key, weight in distance_weights.items():
                # Wrap the index of edge items
                wrapped_index = (key + i) % len(temp_node_list)
                if (not allow_self_links) and (
                        temp_node_list[wrapped_index].name == node.name):
                    continue
                node.add_link(temp_node_list[wrapped_index], weight)

        graph.add_nodes(temp_node_list, merge_existing_names=merge_same_words)
        return graph
