#!/usr/bin/env python

import random

from chance import rand

class Link:
    def __init__(self, target, weight):
        """
        :param target: Node instance
        :param weight: Int
        """
        self.target = target
        self.weight = weight
        self.target_name = target.name

    def add_weight(self, amount=1):
        self.weight += amount

    def __str__(self):
        return str(self.target)


class Node:
    def __init__(self, name=None, parent=None, self_destruct=False):
        """
        :param name: str or int, becomes the name and name of the node
        :param parent: instance of Graph to which this node belongs (potentially usable to let nodes
                        trigger network-level events or modifications
        """
        self.name = name
        self.self_destruct = self_destruct
        self.use_weight = 1
        self.link_list = []
        # TODO: implement negative link weights - ie, make is possible to say two punctuations shouldnt come in a row..

    def find_link(self, target_value):
        for link in self.link_list:
            if link.target.value == target_value:
                return link
        # If we've made it this far without returning, it means no matching link was found. Return False.
        return False

    def add_link(self, target, weight=1):
        """
        :param target: Node or list of Nodes
        :param weight: weight (applied to all if target is a list
        """
        # Check to make sure there isn't already a link to the target node
        if isinstance(target, list):
            for target_item in target:
                already_exists = False
                if weight < 0:
                    weight = 0
                for link in self.link_list:
                    if link.target == target_item:
                        already_exists = True
                        link.add_weight(weight)
                        link.target.use_weight += 1
                        break
                if not already_exists:
                    self.link_list.append(Link(target_item, weight))
        else:
            already_exists = False
            if weight < 0:
                weight = 0
            for link in self.link_list:
                if link.target == target:
                    already_exists = True
                    link.add_weight(weight)
                    link.target.use_weight += 1
                    break
            if not already_exists:
                self.link_list.append(Link(target, weight))

    def add_link_to_self(self, source, weight):
        """
        Adds a real link from source node to self at given weight
        :param source: Node instance
        :param weight: weight of both links
        :return: False if failed, otherwise None
        """
        # If target is just one object and not a list
        if not isinstance(source, list):
            if not isinstance(source, Node):
                print("ERROR: non-node object is being passed to Node.add_real_reciprocal_link(), ignoring...")
                return False
            source.add_link(self, weight=weight)
        # (else) If target is a list, cycle through and do the same to every node in target[]
        else:
            for source_node in source:
                if not isinstance(source_node, Node):
                    print("ERROR: non-node object is being passed to Node.add_real_reciprocal_link(), ignoring...")
                    return False
                source_node.add_link(self, weight=weight)

    def add_reciprocal_link(self, target, weight):
        """
        Adds a link to self pointing to target, and to target pointing to self of equal weight
        :param target: Node object or list of Node objects
        :param weight: weight of both links
        :return: False if failed, otherwise None
        """
        # If target is just one object and not a list
        if not isinstance(target, list):
            if not isinstance(target, Node):
                print("ERROR: non-node object is being passed to Node.add_real_reciprocal_link(), ignoring...")
                return False
            self.add_link(target, weight)
            target.add_link(self, weight)
        # (else) If target is a list, cycle through and do the same to every node in target[]
        else:
            for node in target:
                self.add_reciprocal_link(node, weight)

    def remove_links_to_self(self):
        self.link_list[:] = [link for link in self.link_list if link.target != self]

    def get_value(self):
        return self.name


class NoteBehavior(Node):
    # For use as Node objects in a Graph, allows continuous relationship-based behavior for notes
    def __init__(self, name=None, direction=None, special_action=None,
                 interval_weights=None, pitch_set=None, count_intervals_by_slots=False):
        """
        :param direction: Integer, -1 for down, 1 for up, 0 for either
        :param interval_weights: array of Weight objects or tuples standing in place of them
        :param pitch_set: list of available pitches (diatonic, octatonic, etc.)
        :return:
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
                new_pitch = min(self.pitch_set, key=lambda p: abs(p - approx_pitch))
                return new_pitch
            # Otherwise just return the already found approx_pitch
            else:
                return approx_pitch
        else:
            # If self.count_interval_by_slots is True, then treat interval as steps along self.pitch_set
            pitch_set = sorted(self.pitch_set)
            # If start_pitch isn't in sorted pitch_set, snap it to the closest
            if start_pitch not in pitch_set:
                start_pitch = min(pitch_set, key=lambda p: abs(p - start_pitch))
            # Find the index in pitch_set to which start_pitch fits now
            start_index = -1
            i = 0
            while i < len(pitch_set):
                if start_pitch == pitch_set[i]:
                    start_index = i
                    break
                i += 1
            if start_index == -1:
                print("WARNING: matching pitch wasn't found in NoteBehavior.move_pitch()")
            # Find the slot_interval to move along the pitch_set by
            slot_interval = rand.weighted_curve_rand(self.interval_weights, True)
            # Make sure to invert direction if needed
            if self.direction == -1:
                slot_interval *= -1
            elif self.direction == 0:
                # If direction == 0 (either), roll heads or tails to determine if slot_interval should invert
                if random.randint(0, 1) == 0:
                    slot_interval *= -1
            # Finally, add adjusted slot_interval to start_index, and use it to find the return_pitch, and return it
            return_index = start_index + slot_interval
            # Special handling in can return_index goes out of the bounds of pitch_set: snap to nearest outer
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
    def __init__(self, name=None, alignment='left', left_indent=0, right_indent=0):
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
