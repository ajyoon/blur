"""A module containing a model Markov graph.
::
    >>> from blur.markov.node import Node
    >>> node_1 = Node('One')
    >>> node_2 = Node('Two')
    >>> node_1.add_link(node_1, 5)
    >>> node_1.add_link(node_2, 2)
    >>> node_2.add_link(node_1, 1)
    >>> graph = Graph([node_1, node_2])
    >>> [graph.pick().get_value() for i in range(10)]        # doctest: +SKIP
    ['One', 'One', 'One', 'One', 'One', 'One', 'Two', 'One', 'One', 'One']
"""

from __future__ import division
import random
import re

from blur.rand import weighted_choice, weighted_rand
from blur.markov.node import Node


class Graph:
    """
    A Markov graph with a number of handy utilities.

    The graph consists of a list of ``Node`` 's and keeps track of
    which node was picked last.

    Several utilities offer conveniences for managing the network.
    """

    def __init__(self, node_list=None):
        """
        Args:
            node_list (list): An optional list of nodes to
                populate the network with. To populate the network after
                initialization, use the ``Graph.add_nodes()`` method.

        Warning:
            Nodes are not copied when placed into the graph:
            the passed nodes are used in the object.
            Side effects may occur if node-altering methods are called,
            such as ``Graph.apply_noise()`` or ``Graph.feather_links()``.
            Handle with care if using the same ``Node`` in multiple contexts.
        """
        self.current_node = None
        self.node_list = []
        if node_list:
            self.add_nodes(node_list)

    def __str__(self):
        node_list = ''.join(['\n    {}: {}'.format(i, n.value)
                             for i, n in enumerate(self.node_list)])
        return ('graph.Graph instance with {} nodes:{}'.format(
                    len(self.node_list),
                    node_list
            )
        )

    def merge_nodes(self, keep_node, kill_node):
        """
        Merge two nodes in the graph.

        Takes two nodes and merges them together, merging their links by
        combining the two link lists and summing the weights of links which
        point to the same node.

        All links in the graph pointing to ``kill_node`` will be merged
        into ``keep_node``.

        Links belonging to ``kill_node`` which point to targets not in
        ``self.node_list`` will not be merged into ``keep_node``

        Args:
            keep_node (Node): node to be kept
            kill_node (Node): node to be deleted

        Returns: None

        Example:
            >>> from blur.markov.node import Node
            >>> node_1 = Node('One')
            >>> node_2 = Node('Two')
            >>> node_3 = Node('Three')
            >>> node_1.add_link(node_3, 7)
            >>> node_2.add_link(node_1, 1)
            >>> node_2.add_link(node_2, 3)
            >>> node_3.add_link(node_2, 5)
            >>> graph = Graph([node_1, node_2, node_3])
            >>> print([node.value for node in graph.node_list])
            ['One', 'Two', 'Three']
            >>> graph.merge_nodes(node_2, node_3)
            >>> print([node.value for node in graph.node_list])
            ['One', 'Two']
            >>> for link in graph.node_list[1].link_list:
            ...     print('{} {}'.format(link.target.value, link.weight))
            One 1
            Two 8
        """
        # Merge links from kill_node to keep_node
        for kill_link in kill_node.link_list:
            if kill_link.target in self.node_list:
                keep_node.add_link(kill_link.target, kill_link.weight)
        # Merge any links in the graph pointing to kill_node into links
        # pointing to keep_node
        for node in self.node_list:
            for link in node.link_list:
                if link.target == kill_node:
                    node.add_link(keep_node, link.weight)
                    break
        # Remove kill_node from the graph
        self.remove_node(kill_node)

    def add_nodes(self, nodes):
        """
        Add a given node or list of nodes to self.node_list.

        Args:
            node (Node or list[Node]): the node or list of nodes to add
                to the graph

        Returns: None

        Examples:

        Adding one node: ::

            >>> from blur.markov.node import Node
            >>> graph = Graph()
            >>> node_1 = Node('One')
            >>> graph.add_nodes(node_1)
            >>> print([node.value for node in graph.node_list])
            ['One']

        Adding multiple nodes at a time in a list: ::

            >>> from blur.markov.node import Node
            >>> graph = Graph()
            >>> node_1 = Node('One')
            >>> node_2 = Node('Two')
            >>> graph.add_nodes([node_1, node_2])
            >>> print([node.value for node in graph.node_list])
            ['One', 'Two']
        """
        # Generalize nodes to a list
        if not isinstance(nodes, list):
            add_list = [nodes]
        else:
            add_list = nodes
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

        Example:
            >>> from blur.markov.node import Node
            >>> node_1 = Node('One')
            >>> node_2 = Node('Two')
            >>> node_1.add_link(node_2, 1)
            >>> node_2.add_link(node_1, 1)
            >>> graph = Graph([node_1, node_2])
            >>> for link in graph.node_list[0].link_list:
            ...     print('{} {}'.format(link.target.value, link.weight))
            Two 1
            >>> graph.feather_links(include_self=True)
            >>> for link in graph.node_list[0].link_list:
            ...     print('{} {}'.format(link.target.value, link.weight))
            Two 1
            One 0.01
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
            noise_weights (list): a list of weight tuples
                of form ``(float, float)`` corresponding to
                ``(amount, weight)`` describing the noise to be
                added to each link in the graph
            uniform_amount (float): the maximum amount of uniform noise
                to be applied if ``noise_weights`` is not set

        Returns: None

        Example:
            >>> from blur.markov.node import Node
            >>> node_1 = Node('One')
            >>> node_2 = Node('Two')
            >>> node_1.add_link(node_1, 3)
            >>> node_1.add_link(node_2, 5)
            >>> node_2.add_link(node_1, 1)
            >>> graph = Graph([node_1, node_2])
            >>> for link in graph.node_list[0].link_list:
            ...     print('{} {}'.format(link.target.value, link.weight))
            One 3
            Two 5
            >>> graph.apply_noise()
            >>> for link in graph.node_list[0].link_list:
            ...     print('{} {}'.format(
            ...         link.target.value, link.weight))       # doctest: +SKIP
            One 3.154
            Two 5.321
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

    def find_node_by_value(self, value):
        """
        Find and return a node in self.node_list with the value ``value``.

        If multiple nodes exist with the value ``value``,
        return the first one found.

        If no such node exists, this returns ``None``.

        Args:
            value (Any): The value of the node to find

        Returns:
            Node: A node with value ``value`` if it was found

            None: If no node exists with value ``value``

        Example:
            >>> from blur.markov.node import Node
            >>> node_1 = Node('One')
            >>> graph = Graph([node_1])
            >>> found_node = graph.find_node_by_value('One')
            >>> found_node == node_1
            True
        """
        try:
            return next(n for n in self.node_list if n.value == value)
        except StopIteration:
            return None

    def remove_node(self, node):
        """
        Remove a node from ``self.node_list`` and links pointing to it.

        If ``node`` is not in the graph, do nothing.

        Args:
            node (Node): The node to be removed

        Returns: None

        Example:
            >>> from blur.markov.node import Node
            >>> node_1 = Node('One')
            >>> graph = Graph([node_1])
            >>> graph.remove_node(node_1)
            >>> len(graph.node_list)
            0
        """
        if node not in self.node_list:
            return
        self.node_list.remove(node)
        # Remove links pointing to the deleted node
        for n in self.node_list:
            n.link_list = [link for link in n.link_list if
                           link.target != node]

    def remove_node_by_value(self, value):
        """
        Delete all nodes in ``self.node_list`` with the value ``value``.

        Args:
            value (Any): The value to find and delete owners of.

        Returns: None

        Example:
            >>> from blur.markov.node import Node
            >>> node_1 = Node('One')
            >>> graph = Graph([node_1])
            >>> graph.remove_node_by_value('One')
            >>> len(graph.node_list)
            0
        """
        self.node_list = [node for node in self.node_list
                          if node.value != value]
        # Remove links pointing to the deleted node
        for node in self.node_list:
            node.link_list = [link for link in node.link_list if
                              link.target.value != value]

    def has_node_with_value(self, value):
        """
        Whether any node in ``self.node_list`` has the value ``value``.

        Args:
            value (Any): The value to find in ``self.node_list``

        Returns: bool

        Example:
            >>> from blur.markov.node import Node
            >>> node_1 = Node('One')
            >>> graph = Graph([node_1])
            >>> graph.has_node_with_value('One')
            True
            >>> graph.has_node_with_value('Foo')
            False
        """
        for node in self.node_list:
            if node.value == value:
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
            starting_node (Node): ``Node`` to pick from.

        Returns: Node

        Example:
            >>> from blur.markov.node import Node
            >>> node_1 = Node('One')
            >>> node_2 = Node('Two')
            >>> node_1.add_link(node_1, 5)
            >>> node_1.add_link(node_2, 2)
            >>> node_2.add_link(node_1, 1)
            >>> graph = Graph([node_1, node_2])
            >>> [graph.pick().get_value() for i in range(5)]   # doctest: +SKIP
            ['One', 'One', 'Two', 'One', 'One']
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
    def from_string(cls,
                    source,
                    distance_weights=None,
                    merge_same_words=False,
                    group_marker_opening='<<',
                    group_marker_closing='>>'):
        """
        Read a string and derive of ``Graph`` from it.

        Words and punctuation marks are made into nodes.

        Punctuation marks are split into separate nodes unless they fall
        between other non-punctuation marks. ``'hello, world'`` is split
        into ``'hello'``, ``','``, and ``'world'``, while ``'who's there?'``
        is split into ``"who's"``, ``'there'``, and ``'?'``.

        To group arbitrary characters together into a single node
        (e.g. to make ``'hello, world!'``), surround the
        text in question with ``group_marker_opening`` and
        ``group_marker_closing``. With the default value, this
        would look like ``'<<hello, world!>>'``. It is recommended that
        the group markers not appear anywhere in the source text where they
        aren't meant to act as such to prevent unexpected behavior.

        The exact regex for extracting nodes is defined by: ::

            expression = r'{0}(.+){1}|([^\w\s]+)\B|([\S]+\b)'.format(
                ''.join('\\' + c for c in group_marker_opening),
                ''.join('\\' + c for c in group_marker_closing)
            )

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

                The default value for ``distance_weights`` is ``{1: 1}``.
                This means that each word gets equal weight to whatever
                word follows it. Consequently, if this default value is
                used and ``merge_same_words`` is ``False``, the resulting
                graph behavior will simply move linearly through the
                source, wrapping at the end to the beginning.

            merge_same_words (bool): if nodes which have the same value should
                be merged or not.
            group_marker_opening (str): The string used to mark the beginning
                of word groups.
            group_marker_closing (str): The string used to mark the end
                of word groups. It is strongly recommended that this be
                different than ``group_marker_opening`` to prevent unexpected
                behavior with the regex pattern.

        Returns: Graph

        Example:
            >>> graph = Graph.from_string('i have nothing to say and '
            ...                           'i am saying it and that is poetry.')
            >>> ' '.join(graph.pick().value for i in range(8)) # doctest: +SKIP
            'using chance algorithmic in algorithmic art easier blur'
        """
        if distance_weights is None:
            distance_weights = {1: 1}
        # Convert distance_weights to a sorted list of tuples
        # To make output node list order more predictable
        sorted_weights_list = sorted(distance_weights.items(),
                                     key=lambda i: i[0])
        # regex that matches:
        #   * Anything surrounded by
        #       group_marker_opening and group_marker_closing,
        #   * Groups of punctuation marks followed by whitespace
        #   * Any continuous group of non-whitespace characters
        #       followed by whitespace
        expression = r'{0}(.+){1}|([^\w\s]+)\B|([\S]+\b)'.format(
            ''.join('\\' + c for c in group_marker_opening),
            ''.join('\\' + c for c in group_marker_closing)
        )
        matches = re.findall(expression, source)
        # Un-tuple matches since we are only using groups to strip brackets
        # Is there a better way to do this?
        words = [next(t for t in match if t) for match in matches]

        if merge_same_words:
            # Ensure a 1:1 correspondence between words and nodes,
            # and that all links point to these nodes as well

            # Create nodes for every unique word
            temp_node_list = []
            for word in words:
                if word not in (n.value for n in temp_node_list):
                    temp_node_list.append(Node(word))
            # Loop through words, attaching links to nodes which correspond
            # to the current word. Ensure links also point to valid
            # corresponding nodes in the node list.
            for i, word in enumerate(words):
                matching_node = next(
                    (n for n in temp_node_list if n.value == word))
                for key, weight in sorted_weights_list:
                    # Wrap the index of edge items
                    wrapped_index = (key + i) % len(words)
                    target_word = words[wrapped_index]
                    matching_target_node = next(
                        (n for n in temp_node_list
                         if n.value == target_word))
                    matching_node.add_link(matching_target_node, weight)
        else:
            # Create one node for every (not necessarily unique) word.
            temp_node_list = [Node(word) for word in words]
            for i, node in enumerate(temp_node_list):
                for key, weight in sorted_weights_list:
                    # Wrap the index of edge items
                    wrapped_index = (key + i) % len(temp_node_list)
                    node.add_link(temp_node_list[wrapped_index], weight)

        graph = cls()
        graph.add_nodes(temp_node_list)
        return graph

    @classmethod
    def from_file(cls,
                  source,
                  distance_weights=None,
                  merge_same_words=False,
                  group_marker_opening='<<',
                  group_marker_closing='>>'):
        """
        Read a string from a file and derive a ``Graph`` from it.

        This is a convenience function for opening a file and passing its
        contents to ``Graph.from_string()`` (see that for more detail)

        Args:
            source (str): the file to read and derive the graph from
            distance_weights (dict): dict of relative indices corresponding
                with word weights. See ``Graph.from_string`` for more detail.
            merge_same_words (bool): whether nodes which have the same value
                should be merged or not.
            group_marker_opening (str): The string used to mark the beginning
                of word groups.
            group_marker_closing (str): The string used to mark the end
                of word groups.

        Returns: Graph

        Example:
            >>> graph = Graph.from_file('cage.txt')            # doctest: +SKIP
            >>> ' '.join(graph.pick().value for i in range(8)) # doctest: +SKIP
            'poetry i have nothing to say and i'
        """
        source_string = open(source, 'r').read()
        return cls.from_string(source_string,
                               distance_weights,
                               merge_same_words,
                               group_marker_opening=group_marker_opening,
                               group_marker_closing=group_marker_closing)
