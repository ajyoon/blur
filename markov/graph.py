#!/usr/bin/env python

import random

from chance.rand import weighted_option_rand
from . import nodes


class Network:
    def __init__(self, name=None):
        self.node_list = []
        self.source = None
        self.output_node_sequence = []
        self.name = name
        self.current_node = None
        self.previous_node = None
        self.input_sequence = []
        self.weight = None
        self.chance_to_leave = None
        self._allow_self_links = True

    def merge_nodes(self, keep_node, kill_node):
        """
        Takes two nodes and merges them together, merging their links by combining the two link lists and
         summing the weights of links which point to the same node
        :param keep_node: instance of chance.nodes.Node (or subclass) to be kept
        :param kill_node: instance of chance.nodes.Node (or subclass) to be deleted
        :return:
        """
        assert isinstance(keep_node, nodes.Node)
        assert isinstance(kill_node, nodes.Node)
        merge_index = 0
        for kill_link in kill_node.link_list:
            duplicate_found = False
            i = 0
            while i < len(keep_node.link_list):
                if str(kill_link.target) == str(keep_node.link_list[i].target):
                    duplicate_found = True
                    merge_index = i
                    break
                i += 1
            if duplicate_found:
                keep_node.link_list[merge_index].weight += kill_link.weight
            else:
                keep_node.add_link(kill_link.target, kill_link.weight)

    def add_nodes(self, node):
        """
        Adds a given node or list of nodes to self.node_list - if a node already exists in the network, merge them
        :param node: Node instance or list of Node instances
        :return:
        """
        if not isinstance(node, list):
            add_list = [node]
        else:
            add_list = node

        for add_node in add_list:
            if self._allow_self_links:
                self.node_list.append(add_node)
            else:
                for currently_existing_node in self.node_list:
                    if currently_existing_node.name == add_node.name:
                        self.merge_nodes(currently_existing_node, add_node)
                        break
                else:
                    self.node_list.append(add_node)

    def feather_links(self, factor=0.01, include_self=False):
        """
        Goes through every node in the network and adds their linked nodes' links multiplied by given factor
        :param factor: multiplier of neighbor links
        :param include_self: Bool, determines if nodes can be feathered to themselves
        :return: None
        """
        # TODO: Build me!
        pass


    def apply_noise(self, max_factor=0.1):
        """
        Goes through every node in the network, adding random amounts to every link scaled to its weight and max_factor
        :param max_factor: float
        :return:
        """
        # Some simple type handling
        if isinstance(max_factor, int):
            max_factor *= 1.0
        # Main node loop
        for node in self.node_list:
            for link in node.link_list:
                link.weight += round(random.uniform(0, link.weight * max_factor), 3)

    def refresh_links(self, copy_network):
        # Is this necessary???
        # Finds every duplicate node from self and copy_network, and replaces links in duplicate nodes
        for copy_node in copy_network.node_list:
            for keep_node in self.node_list:
                if copy_node.name == keep_node.name:
                    keep_node.link_list = copy_node.link_list

    def find_node_by_name(self, name):
        for node in self.node_list:
            if node.name == name:
                return node
        else:
            raise ValueError('Could not find node by name ' + str(name))

    def remove_node_by_name(self, name):
        """
        Deletes a node by a given name and all network links pointing to it
        :param name: str
        """
        # Remove the node from self.node_list
        self.node_list[:] = [node for node in self.node_list if (not node.name == name)]
        # Look through every link in the network, removing all references to the newly removed node
        for node in self.node_list:
            node.link_list[:] = [link for link in node.link_list if (not link.target_name == name)]

    def has_node_with_name(self, name):
        """
        Checks to see if any node in self.node_list has the same Node.name as name
        :param name: str or int
        :return: Bool
        """
        for node in self.node_list:
            if node.name == name:
                return True
        else:
            return False

    def pick_by_use_weight(self):
        """
        :return: Node instance
        """
        self.previous_node = self.current_node
        node = weighted_option_rand([(n.name, n.use_weight)for n in
                                  self.node_list])
        self.current_node = self.find_node_by_name(node)
        return self.current_node


    def pick(self, current_node=None):
        """
        Picks the next node for the network based on a starting node which is
        either explicitly stated or implicitly found according to these rules:

            - if current_node is specified, start from there
            - if current_node is None, start from self.current_node
            - if current_node is None and self.current_node is None, pick from the network's nodes' use weights

        :param current_node: Node object, or None to pick according to self.current_node
        :return: Next node
        """
        self.previous_node = self.current_node
        # If None was passed (default), start from self.current_node
        if current_node is None:
            if self.current_node is not None:
                current_node = self.current_node
            else:
                return self.pick_by_use_weight()
        # Otherwise, use a discreet weighted random on start_node.link_list
        self.current_node = weighted_option_rand([(link.target, link.weight)
                                                  for link in current_node.link_list])
        return self.current_node

    def walk(self, steps):
        """
        Populates self.output_node_sequence by walking along the network, picking from node to node
        :param steps: int, how many nodes to pick
        """
        assert self.node_list != []
        for i in range(steps):
            self.output_node_sequence.append(self.pick())



def word_mine(source, relationship_weights=None, allow_self_links=True, merge_same_words=False):
    """
    Reads a text document and generates a Network object based on it
    :param source: str, either path to a .docx file or a string literal
    :param relationship_weights: dict of relative indices corresponding with word weights.
                                  For example, if a dict entry is '1: 1000' this means that every word is linked to the
                                  word which follows it with a weight of 1000. '-4: 350' would mean that every word is
                                  linked to the 4th word behind it with a weight of 350
    :param allow_self_links: Bool - determines if words are allowed to follow themselves in the output network
    :param merge_same_words: Bool - determines if nodes which have the same value should be merged or not
                                     False means that the resulting network will move much more continuously through
                                     the source material, while True means that the network will move much more
                                     erratically. For example - if a very common word, such as "the" is encountered,
                                     the network jump to a highly unpredictable place because all occurences of "the"
                                     are grouped into one node.
                                     Note that this is pretty computationally expensive
    :return: instance of Network
    """
    punctuation_list = [' ', ',', '.', ';', '!', '?', ':']
    action_list = ['+']
    node_sequence = []
    network = Network()
    network.source = source

    # Set up relative position weights
    if relationship_weights is None:
        distance_weights = {1: 1000, 2: 100, 3: 80, 4: 60, 5: 50,
                            6: 40, 7: 30, 8: 17, 9: 14, 10: 10,
                            11: 10, 12: 10, 13: 5, 14: 5, 15: 75}

    file_string = open(source).read()

    # Parse the file_string, sending words, punctuations, and actions
    # to node_sequence in the order they appear
    temp_string = ""
    i = 0
    while i < len(file_string):
        # If the character belongs in the punctuation list
        if file_string[i] in punctuation_list:
            # Send anything in temp_string to a new word
            if temp_string != '':
                node_sequence.append(nodes.Word(temp_string))
                temp_string = ''
            # If a space is encountered, skip it
            # Otherwise, add the punctuation character to word_list
            if not file_string[i] == ' ':
                node_sequence.append(nodes.Punctuation(file_string[i]))
                temp_string = ''

        elif file_string[i] in action_list:
            # Send anything in temp_string to a new word
            if temp_string != '':
                node_sequence.append(nodes.Word(temp_string))
                temp_string = ''
            node_sequence.append(nodes.Action(file_string[i]))

        # If special < character is encountered, indicating word groups
        elif file_string[i] == '<':
            # Send temp_string to the word_list and clear temp_string
            if temp_string != '':
                node_sequence.append(nodes.Word(temp_string))
                temp_string = ''
            # Skip over < character
            i += 1
            # Loop until end of word group is reached (marked by >)
            while file_string[i] != '>':
                temp_string += file_string[i]
                i += 1
            # Send new temp_string to another word in the word_list
            node_sequence.append(nodes.Word(temp_string))
            # @ at the end of a word group will indicate that the word self-destructs after it appears once in usage
            if node_sequence[-1].name[-1] == '@':
                node_sequence[-1].name = node_sequence[-1].name[:-1]
                node_sequence[-1].self_destruct = True
            temp_string = ""
            # Skip over > character
            i += 1

        # If we've reached the final character in the file,
        # send whatever remains in temp_string to to a node
        elif i == len(file_string) - 1 and temp_string != '':
            temp_string += file_string[i]
            node_sequence.append(nodes.Word(temp_string))
            temp_string = ''
        else:
            # Add the next character in the file to temp_string
            temp_string += file_string[i]
        i += 1

    if merge_same_words:
        # Send a copy of node_sequence to network, but remove all duplicate nodes first
        for node in node_sequence:
            if not network.has_node_with_name(node.name):
                network.node_list.append(node)

        # Now use the ordered (and still containing same-name nodes) node_sequence to build the links in network
        for i in range(len(node_sequence)):
            for x in distance_weights.keys():
                wrapping_index = (i + x)
                if wrapping_index >= len(node_sequence):
                    wrapping_index = - (wrapping_index - len(node_sequence))
                network.find_node_by_name(node_sequence[i].name).add_link(
                    network.find_node_by_name(node_sequence[wrapping_index].name), distance_weights[x])
    else:
        network.add_nodes(node_sequence)
        # Within network.node_list, find all relationships according to distance_weights
        for i in range(len(network.node_list)):
            for x in distance_weights.keys():
                # Use a wrapping index so that the source material circles on itself
                # This is useful for preventing the network from getting stuck at the beginning or end of the source
                # It's also cool
                wrapping_index = (i + x)
                while wrapping_index >= len(network.node_list):
                    wrapping_index = - (wrapping_index - len(network.node_list))
                while wrapping_index <= -1 * len(network.node_list):
                    wrapping_index += len(network.node_list)
                network.node_list[i].add_link(network.node_list[wrapping_index], distance_weights[x])

    # Special handling for \n node: remove all links to Punctuation objects
    for node in network.node_list:
        if node.name == '\n':
            node.link_list[:] = [link for link in node.link_list if link.target.name not in punctuation_list]

    # if self_links have been disabled, remove all self referential links (except for blank lines)
    if not allow_self_links:
        for node in network.node_list:
            if node.name != '\n':
                node.remove_links_to_self()

    return network

