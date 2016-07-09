"""
UNDER RECONSTRUCTION - APOLOGIES FOR THE MESS
"""

import random

from chance import rand


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
        self.use_weight = 1
        self.link_list = []

    def find_link(self, target_value):
        for link in self.link_list:
            if link.target.value == target_value:
                return link
        else:
            return False

    def add_link(self, targets, weight=1):
        """
        Args:
            targets (Node or list[Node]): node or nodes to link to
            weight (int or float): weight for the new link(s)
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


###############################################################################
# Basic Nodes
#
# Should probably move to another module, or entirely out of the package...
###############################################################################


class NoteBehavior(Node):
    """For use as Node objects in a Graph.
    Allows continuous relationship-based behavior for notes"""

    def __init__(self, name=None, direction=None, special_action=None,
                 interval_weights=None, pitch_set=None,
                 count_intervals_by_slots=False):
        """
        Args:
            direction (int): -1 for down, 1 for up, 0 for either
            interval_weights (list[Weight or tuple repr. of Weight]):
            pitch_set (list[int]): ????
        """
        Node.__init__(self, name=name)
        self.direction = direction
        self.special_action = special_action
        self.interval_weights = interval_weights
        self.pitch_set = pitch_set
        self.count_intervals_by_slots = count_intervals_by_slots

    def get_value(self):
        return None

    def move_pitch(self, start_pitch):

        if not self.count_intervals_by_slots:
            # Roll interval based on self.weights
            interval = rand.weighted_curve_rand(self.interval_weights, True)
            # Make sure to invert direction if needed
            if self.direction == -1:
                interval *= -1
            # Add adjusted interval to start_pitch
            approx_pitch = start_pitch + interval
            # If self.pitch_set is defined, fit adjusted interval to it
            if self.pitch_set is not None:
                new_pitch = min(self.pitch_set,
                                key=lambda p: abs(p - approx_pitch))
                return new_pitch
            # Otherwise just return the already found approx_pitch
            else:
                return approx_pitch
        else:
            # If self.count_interval_by_slots is True,
            # treat interval as steps along self.pitch_set
            pitch_set = sorted(self.pitch_set)
            # If start_pitch isn't in sorted pitch_set, snap it to the closest
            if start_pitch not in pitch_set:
                start_pitch = min(pitch_set,
                                  key=lambda p: abs(p - start_pitch))
            # Find the index in pitch_set to which start_pitch fits now
            start_index = -1
            i = 0
            while i < len(pitch_set):
                if start_pitch == pitch_set[i]:
                    start_index = i
                    break
                i += 1
            if start_index == -1:
                # TODO: Replace with exception
                print("WARNING: matching pitch wasn't"
                      "found in NoteBehavior.move_pitch()")
            # Find the slot_interval to move along the pitch_set by
            slot_interval = rand.weighted_curve_rand(
                self.interval_weights, True)
            # Make sure to invert direction if needed
            if self.direction == -1:
                slot_interval *= -1
            elif self.direction == 0:
                # randomly determine if slot_interval should invert
                if random.randint(0, 1) == 0:
                    slot_interval *= -1
            # add adjusted slot_interval to start_index,
            # use it to find the return_pitch, and return it
            return_index = start_index + slot_interval
            # Special handling in case return_index goes out of the
            # bounds of pitch_set: snap to nearest outer
            if return_index < 0:
                return_index = 0
            elif return_index > (len(pitch_set) - 1):
                return_index = len(pitch_set) - 1

            return pitch_set[return_index]


class NetworkJumper(Node):
    # Not used for anything right now, but could potentially have applications
    def __init__(self, name, target_network):
        Node.__init__(self, name=name)
        self.target_network = target_network

    def get_value(self):
        return self.name


class Image(Node):
    def __init__(self, name=None, alignment='left',
                 left_indent=0, right_indent=0):
        Node.__init__(self, name=name)
        self.alignment = alignment
        self.left_indent = left_indent
        self.right_indent = right_indent

    def get_value(self):
        return self.name


class Word(Node):
    def __init__(self, name=None):
        Node.__init__(self, name=name)

    def get_value(self):
        return self.name


class Punctuation(Node):
    def __init__(self, mark):
        Node.__init__(self, name=mark)

    def get_value(self):
        return self.name


class Value(Node):
    def __init__(self, name):
        Node.__init__(self, name=name)

    def get_value(self):
        return self.name


class WeightListNode(Node):
    def __init__(self, name, weights=None):
        Node.__init__(self, name=name)
        self.weights = weights

    def get_value(self, do_round=True):
        return rand.weighted_curve_rand(self.weights, do_round)


class Action(Node):
    def __init__(self, name):
        Node.__init__(self, name=name)

    def get_value(self):
        return self.name


class BlankLine(Node):
    def __init__(self, name):
        Node.__init__(self, name=name)

    def get_value(self):
        return self.name
