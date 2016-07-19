"""A module containing a model Markov graph."""

from __future__ import division
import random
import re

from blur.rand import weighted_choice, weighted_rand
from . import nodes


class Graph:
    """
    A Markov graph with a number of handy utilities.

    The graph consists of a list of ``Node``s and keeps track of
    which node was picked last.

    Several utilities offer conveniences for managing the network.
    """

    def __init__(self, node_list=None):
        """
        Initialize a graph, optionally populating it with a list of ``Node``s.

        Args:
            node_list (Optional[list]): An optional list of nodes to
                populate the network with. To populate the network after
                initialization, use the ``Graph.add_nodes()`` method.

        Notes:
            The nodes passed here are not copied when placing into
            the graph: the passed nodes are used in the object.
            Side effects may occur if node-altering methods are called,
            such as ``Graph.apply_noise()`` or ``Graph.feather_links()``.
            Handle with care if using the same ``Node`` in multiple contexts.
        """
        self.current_node = None
        self.node_list = []
        if node_list:
            self.add_nodes(node_list)

    def merge_nodes(self, keep_node, kill_node):
        """
        Merge two nodes in the graph.

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

        Optionally, if a ``Node`` being added shares a name with a ``Node``
        that already exists in the ``Graph``, merge the two ``Nodes`` to
        prevent duplicates.

        Args:
            node (Node or list[node]): ``Node``(s) to be added to the graph
            merge_existing_names (Optional[bool]): Whether or not to merge
                any nodes being added with ``Node``s already in the graph
                with the same name (``Node.name``) as the ones being added.

        Returns: None

        Notes:
            The nodes passed here are not copied when placing into
            the graph: the passed nodes are used in the object.
            Side effects may occur if node-altering methods are called,
            such as ``Graph.apply_noise()`` or ``Graph.feather_links()``.
            Handle with care if using the same ``Node`` in multiple contexts.
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
        Find and return a node in self.node_list with the name ``name``.

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
        Remove a node from the graph, removing all links pointing to it.

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
        Delete all nodes in self.node_list with the name ``name``.

        Args:
            name (Any): The name to find and delete owners of.

        Returns: None
        """
        self.node_list = [node for node in self.node_list if node.name != name]
        # Remove links pointing to the deleted node
        for node in self.node_list:
            node.link_list = [link for link in node.link_list if
                              link.target.name != name]

    def has_node_with_name(self, name):
        """
        Whether any node in ``self.node_list`` has the name ``name``.

        Args:
            name (Any): The name to find in ``self.node_list``

        Returns: bool
        """
        for node in self.node_list:
            if node.name == name:
                return True
        else:
            return False

    def pick(self, starting_node=None):
        """
        Pick a node on the graph based on the links in a starting node.

        Additionally, set ``self.current_node`` to the newly picked node.

        * if ``starting_node`` is specified, start from there
        * if ``starting_node`` is ``None``, start from ``self.current_node``
        * if ``starting_node`` is ``None`` and ``self.current_node``
            is ``None``, pick a uniformally random node in ``self.node_list``

        Args:
            starting_node (Optional[Node]): ``Node`` to pick from.

        Returns: Node
        """
        if starting_node is None:
            if self.current_node is None:
                random_node = random.choice(self.node_list)
                self.current_node = random_node
                return random_node
            else:
                starting_node = self.current_node
        # Use weighted_choice on start_node.link_list
        self.current_node = weighted_choice(
            [(link.target, link.weight) for link in starting_node.link_list])
        return self.current_node

    @classmethod
    def from_file(cls,
                  source,
                  distance_weights=None,
                  merge_same_words=False):
        """
        Read a string from a file and generate a Graph object based on it.

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

                The default value for ``distance_weights`` is: ::
                    {1: 1}
                This means that each word gets equal weight to whatever
                word follows it. Consequently, if this default value is
                used and ``merge_same_words`` is ``False``, the resulting
                graph behavior will simply move linearly through the
                source, wrapping at the end to the beginning.
            merge_same_words (bool): if nodes which have the same value should
                be merged or not.

        Returns: Graph
        """
        source_string = open(source, 'r').read()
        return cls.from_string(source_string,
                               distance_weights,
                               merge_same_words)

    @classmethod
    def from_string(cls,
                    source,
                    distance_weights=None,
                    merge_same_words=False):
        """
        Read a string and generate a ``Graph`` object based on it.

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

                The default value for ``distance_weights`` is: ::
                    {1: 1}
                This means that each word gets equal weight to whatever
                word follows it. Consequently, if this default value is
                used and ``merge_same_words`` is ``False``, the resulting
                graph behavior will simply move linearly through the
                source, wrapping at the end to the beginning.

            merge_same_words (bool): if nodes which have the same value should
                be merged or not.

        Returns: Graph
        """
        if distance_weights is None:
            distance_weights = {1: 1}
        # regex that matches:
        #   * Anything surrounded by angle bracks,
        #   * The punctuation marks: , . ; ! ? : \ / ' " ( ) [ ]
        #   * Any continuous group of alphanumerical characters
        expression = '<(.+)>|([,.;!?:\\/\'"()[])|([a-zA-z0-9]+)'
        matches = re.findall(expression, source)
        # Un-tuple matches since we are only using groups to strip brackets
        # Is there a better way to do this?
        words = [next(t for t in match if t) for match in matches]
        temp_node_list = [nodes.Node(w) for w in words]

        for i, node in enumerate(temp_node_list):
            for key, weight in distance_weights.items():
                # Wrap the index of edge items
                wrapped_index = (key + i) % len(temp_node_list)
                node.add_link(temp_node_list[wrapped_index], weight)

        graph = cls()
        graph.add_nodes(temp_node_list, merge_existing_names=merge_same_words)
        return graph
