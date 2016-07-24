"""
Classes for use in ``Graph`` 's.

Besides initializing ``Node`` 's, you will rarely need
to directly interact with these objects, as ``Graph`` provides
much easier and more powerful interactions.
"""

import random

from blur import rand


class Link:
    """
    A one-way link pointing to a ``Node`` with a weight.

    For use in conjunction with the ``Node`` and ``Graph`` classes.
    You will rarely need to deal with ``Link`` 's directly. The best
    way to create a ``Link`` from one ``Node`` to another is
    by calling ``some_node.add_link(another_node, 5)`` instead.
    """

    def __init__(self, target, weight):
        """
        Initialize a link.

        Args:
            target (Node): The ``Node`` this ``Link`` will point to
            weight (float or int): The numerical weight for this ``Link``
        """
        self.target = target
        self.weight = weight


class Node:
    """A node to be used in a Markov graph."""

    def __init__(self, name=None, self_destruct=False):
        """
        Initialize a ``Node``.

        Args:
            name (str or int): Name of the node
            self_destruct (bool): whether this note deletes itself after
                being picked by a graph
        """
        self.name = name
        self.self_destruct = self_destruct
        self.link_list = []

    def merge_links_from(self, other_node, merge_same_name_targets=False):
        """
        Merge links from another node with ``self.link_list``.

        Copy links from another node, merging when copied links point to a
        node which this already links to.

        Args:
            other_node (Node): The node to merge links from
            merge_same_name_targets (bool): Whether or not to merge links
                whose targets have the same name (but are not necessarily
                the same ``Node``). If False, links will only be merged
                when ``link_in_other.target == link_in_self.target``. If True,
                links will be merged when
                ``link_in_other.target.name == link_in_self.target.name``

        Returns: None
        """
        for other_link in other_node.link_list:
            for existing_link in self.link_list:
                if merge_same_name_targets:
                    if other_link.target.name == existing_link.target.name:
                        existing_link.weight += other_link.weight
                        break
                else:
                    if other_link.target == existing_link.target:
                        existing_link.weight += other_link.weight
                        break
            else:
                self.add_link(other_link.target, other_link.weight)

    def find_link(self, target_node):
        """
        Find the link that points to ``target_node`` if it exists.

        If no link in ``self`` points to ``target_node``, return None

        Args:
            target_node (Node): The node to look for in ``self.link_list``

        Returns:
            Link: An existing link pointing to ``target_node`` if found
            None: If no such link exists
        """
        try:
            return next(l for l in self.link_list if l.target == target_node)
        except StopIteration:
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
        Create and add a ``Link`` from a source node to ``self``.

        Args:
            source (Node): The node that will own the new ``Link``
                pointing to ``self``
            weight (int or float): The weight of the newly created ``Link``

        Returns: None
        """
        # Generalize source to a list to simplify code
        if not isinstance(source, list):
            source = [source]
        for source_node in source:
            source_node.add_link(self, weight=weight)

    def add_reciprocal_link(self, target, weight):
        """
        Add links pointing in either direction between ``self`` and ``target``.

        This creates a ``Link`` from ``self`` to ``target`` and a ``Link``
        from ``target`` to ``self`` of equal weight. If ``target`` is a list
        of ``Node`` 's, repeat this for each one.

        Args:
            target (Node or list[Node]):
            weight (int or float):

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
        """
        Remove any link in ``self.link_list`` whose ``target`` is ``self``.

        Returns: None
        """
        self.link_list = [link for link in self.link_list if
                          link.target != self]

    def get_value(self):
        """
        Get the value of this ``Node``.

        For this class, this simply returns ``self.name``, but
        for subclasses with more complex behavior, this could be
        more powerful. For example, a ``Node`` might have a value
        which is a ``SoftColor``, in which case this method could
        return a ``SoftColor.get()`` value.

        Returns: Any
        """
        return self.name
