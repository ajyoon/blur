"""
Node and Link classes for use in markov graphs

Besides initializing ``Node`` 's, you will rarely need
to directly interact with these objects, as ``Graph`` provides
much easier and more powerful interactions.
"""


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
        Args:
            target (Node): The ``Node`` this ``Link`` will point to
            weight (float or int): The numerical weight for this ``Link``
        """
        self.target = target
        self.weight = weight

    def __str__(self):
        return ('node.Link instance pointing to node with value "{}" '
                'with weight {}'.format(
                    self.target.value,
                    self.weight
                    )
                )

    def _short_str(self):
        """A less verbose version of __str__()."""
        return ('{} --> {}'.format(self.weight, self.target.value))


class Node:
    """A node to be used in a Markov graph."""

    def __init__(self, value=None, self_destruct=False):
        """
        Args:
            value (Any): Value of the node
            self_destruct (bool): whether this note deletes itself after
                being picked by a `Graph`
        """
        self.value = value
        self.self_destruct = self_destruct
        self.link_list = []

    def __str__(self):
        link_list = ''.join(['\n    {}: {}'.format(i, link._short_str())
                             for i, link in enumerate(self.link_list)])
        return ('node.Node instance with value {} with {} links:{}'.format(
                    self.value,
                    len(self.link_list),
                    link_list
            )
        )

    def merge_links_from(self, other_node, merge_same_value_targets=False):
        """
        Merge links from another node with ``self.link_list``.

        Copy links from another node, merging when copied links point to a
        node which this already links to.

        Args:
            other_node (Node): The node to merge links from
            merge_same_value_targets (bool): Whether or not to merge links
                whose targets have the same value (but are not necessarily
                the same ``Node``). If False, links will only be merged
                when ``link_in_other.target == link_in_self.target``. If True,
                links will be merged when
                ``link_in_other.target.value == link_in_self.target.value``

        Returns: None

        Example:
            >>> node_1 = Node('One')
            >>> node_2 = Node('Two')
            >>> node_1.add_link(node_1, 1)
            >>> node_1.add_link(node_2, 3)
            >>> node_2.add_link(node_1, 4)
            >>> node_1.merge_links_from(node_2)
            >>> print(node_1)
            node.Node instance with value One with 2 links:
                0: 5 --> One
                1: 3 --> Two
        """
        for other_link in other_node.link_list:
            for existing_link in self.link_list:
                if merge_same_value_targets:
                    if other_link.target.value == existing_link.target.value:
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

        Example:
            >>> node_1 = Node('One')
            >>> node_2 = Node('Two')
            >>> node_1.add_link(node_2, 1)
            >>> link_1 = node_1.link_list[0]
            >>> found_link = node_1.find_link(node_2)
            >>> found_link == link_1
            True
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

        Example:
            >>> node_1 = Node('One')
            >>> node_2 = Node('Two')
            >>> node_1.add_link(node_2, 1)
            >>> new_link = node_1.link_list[0]
            >>> print(new_link)
            node.Link instance pointing to node with value "Two" with weight 1
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

        Example:
            >>> node_1 = Node('One')
            >>> node_2 = Node('Two')
            >>> node_1.add_link_to_self(node_2, 5)
            >>> new_link = node_2.link_list[0]
            >>> print('{} {}'.format(new_link.target.value, new_link.weight))
            One 5
            >>> print(new_link)
            node.Link instance pointing to node with value "One" with weight 5
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

        Example:
            >>> node_1 = Node('One')
            >>> node_2 = Node('Two')
            >>> node_1.add_reciprocal_link(node_2, 5)
            >>> new_link_1 = node_1.link_list[0]
            >>> new_link_2 = node_2.link_list[0]
            >>> print(new_link_1)
            node.Link instance pointing to node with value "Two" with weight 5
            >>> print(new_link_2)
            node.Link instance pointing to node with value "One" with weight 5
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

        Example:
            >>> node_1 = Node('One')
            >>> node_1.add_link(node_1, 5)
            >>> node_1.remove_links_to_self()
            >>> len(node_1.link_list)
            0
        """
        self.link_list = [link for link in self.link_list if
                          link.target != self]

    def get_value(self):
        """
        Get the value of this ``Node``.

        For this class, this simply returns ``self.value``, but
        for subclasses with more complex behavior, this could be
        more powerful. For example, a ``Node`` might have a value
        which is a ``SoftColor``, in which case this method could
        return a ``SoftColor.get()`` value.

        Returns: Any

        Example:
            >>> node_1 = Node('One')
            >>> node_1.get_value()
            'One'
        """
        return self.value
