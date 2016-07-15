"""
UNDER RECONSTRUCTION - APOLOGIES FOR THE MESS
"""

import random

from blur import rand


class Link:
    """
    A link that points to a ``Node`` object with a weight for use
    in ``Graph`` models
    """
    def __init__(self, target, weight):
        """
        Args:
            target (Node):
            weight (float or int):
        """
        self.target = target
        self.weight = weight


class Node:
    def __init__(self, name=None, self_destruct=False):
        """
        Args:
            name (str or int): Name of the node
            self_destruct (bool): whether this note deletes itself after
                being picked by a graph
        """
        self.name = name
        self.self_destruct = self_destruct
        # TODO: decide if use_weight is really necessary. If not, remove.
        self.use_weight = 1
        self.link_list = []

    def find_link(self, target_node):
        """
        Find the link that points to ``target_node`` if it exists.

        If no link in ``self`` points to ``target_node``, return None

        Args:
            target_node (Node): The node to look for in ``self.link_list``

        Returns: Node or None
        """
        for link in self.link_list:
            if link.target == target_node:
                return link
        else:
            return None

    def add_link(self, targets, weight):
        """
        Add link(s) pointing to ``targets``.

        If a link already exists pointing to a target, just add ``weight``
        to that link's weight

        Args:
            targets (Node or list[Node]): node or nodes to link to
            weight (int or float): weight for the new link(s)

        Returns: None
        """
        # Generalize targets to a list to simplify code
        if not isinstance(targets, list):
            target_list = [targets]
        else:
            target_list = targets

        for target in target_list:
            # Check to see if self already has a link to target
            for existing_link in self.link_list:
                if existing_link.target == target:
                    existing_link.weight += weight
                    break
            else:
                self.link_list.append(Link(target, weight))

    def add_link_to_self(self, source, weight):
        """
        Add a link from source node to self at given weight

        Args:
            source (Node):
            weight (Weight or tuple repr. of weight)

        Returns: None
        """
        # Generalize source to a list to simplify code
        if not isinstance(source, list):
            source = [source]
        for source_node in source:
            source_node.add_link(self, weight=weight)

    def add_reciprocal_link(self, target, weight):
        """
        Add a link to self pointing to target,
        and to target pointing to self of equal weight

        Args:
            target (Node or list[Node]):
            weight (weight for new links):

        Returns: None
        """
        # Generalize ``target`` to a list
        if not isinstance(target, list):
            target_list = [target]
        else:
            target_list = target
        for t in target_list:
            self.add_link(t, weight)
            t.add_link(self, weight)

    def remove_links_to_self(self):
        self.link_list = [link for link in self.link_list if
                          link.target != self]

    def get_value(self):
        return self.name
