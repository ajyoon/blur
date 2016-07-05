
"""
UNDER RECONSTRUCTION - APOLOGIES FOR THE MESS
"""

import random

from chance.rand import weighted_option_rand
from . import nodes


class Graph:
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

    def add_nodes(self, nodes):
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
        for add_node in add_list:
            for currently_existing_node in self.node_list:
                if currently_existing_node.name == add_node.name:
                    self.merge_nodes(currently_existing_node, add_node)
                    break
            else:
                self.node_list.append(add_node)

    def feather_links(self, factor=0.01, include_self=False):
        """
        Go through every node in the network and adds their
        linked nodes' links multiplied by given factor

        Args:
            factor (float): multiplier of neighbor links
            include_self (bool): if nodes can be feathered to themselves

        Returns: None
        """
        # TODO: Build me!
        pass

    def apply_noise(self, max_factor=0.1):
        """
        Go through every node in the network, adding noise to every link
        scaled to its weight and max_factor

        TODO: alow a custom noise profile (in the form of a weight list)
            to be passed

        Args:
            max_factor (float):

        Returns: None
        """
        # Main node loop
        for node in self.node_list:
            for link in node.link_list:
                link.weight += round(random.uniform(
                    0, link.weight * max_factor), 3)

    def find_node_by_name(self, name):
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

    # TODO: Delete me after refactoring word_mine
    def remove_node_by_name(self, name):
        """
        Deletes a node by a given name and all network links pointing to it
        :param name: str
        """
        self.node_list = [node for node in self.node_list if node.name != name]
        # Remove links pointing to the deleted node
        for node in self.node_list:
            node.link_list = [link for link in node.link_list if
                              link.target_name != name]

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
        :return: Node instance
        """
        self.previous_node = self.current_node
        node = weighted_option_rand([(n.name, n.use_weight)
                                     for n in self.node_list])
        self.current_node = self.find_node_by_name(node)
        return self.current_node

    def pick(self, current_node=None):
        """
        Pick the next node for the network based on a starting node which is
        either explicitly stated or implicitly found according to these rules:

            * if current_node is specified, start from there
            * if current_node is None, start from self.current_node
            * if current_node is None and self.current_node is None,
              pick from the network's nodes' use weights

        Args:
            current_node (Optional[Node]): Node to pick from.

        Returns: Node
        """
        self.previous_node = self.current_node
        # If None was passed (default), start from self.current_node
        if current_node is None:
            if self.current_node is not None:
                current_node = self.current_node
            else:
                return self.pick_by_use_weight()
        # Otherwise, use a discreet weighted random on start_node.link_list
        self.current_node = weighted_option_rand(
            [(link.target, link.weight) for link in current_node.link_list])
        return self.current_node

    def walk(self, steps):
        """
        Populate self.output_node_sequence by walking along the network,
        picking from node to node

        Args:
            steps (int): number of nodes to pick
        """
        for i in range(steps):
            self.output_node_sequence.append(self.pick())


def word_mine(source,
              distance_weights=None,
              allow_self_links=True,
              merge_same_words=False):
    """
    Read a text document and generates a Graph object based on it

    Args:
        source (str): path to the source document
        distance_weights (dict): dict of relative indices corresponding with
            word weights. For example, if a dict entry is '1: 1000' this means
            that every word is linked to the word which follows it with a
            weight of 1000. '-4: 350' would mean that every word is
            linked to the 4th word behind it with a weight of 350
        allow_self_links (bool): if words can be linked to themselves
        merge_same_words (bool): if nodes which have the same value should be
            merged or not.
    
    Returns: Graph
    """
    punctuation_list = [' ', ',', '.', ';', '!', '?', ':']
    action_list = ['+']
    node_sequence = []
    network = Graph()
    network.source = source

    # Set up relative position weights
    if distance_weights is None:
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
            # @ at the end of a word group will indicate that the word
            # self-destructs after it appears once in usage
            if node_sequence[-1].name.endswith('@'):
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
        # Send a copy of node_sequence to network,
        # but remove all duplicate nodes first
        for node in node_sequence:
            if not network.has_node_with_name(node.name):
                network.node_list.append(node)

        # Now use the ordered (and still containing same-name nodes)
        # node_sequence to build the links in network
        for i in range(len(node_sequence)):
            for x in distance_weights.keys():
                wrap_index = (i + x)
                if wrap_index >= len(node_sequence):
                    wrap_index = - (wrap_index - len(node_sequence))
                network.find_node_by_name(node_sequence[i].name).add_link(
                    network.find_node_by_name(node_sequence[wrap_index].name),
                    distance_weights[x])
    else:
        network.add_nodes(node_sequence)
        # Find all relationships according to distance_weights
        for i in range(len(network.node_list)):
            for x in distance_weights.keys():
                # Make indexes circular to prevent IndexErrors
                wrap_index = (i + x)
                while wrap_index >= len(network.node_list):
                    wrap_index = - (wrap_index - len(network.node_list))
                while wrap_index <= -1 * len(network.node_list):
                    wrap_index += len(network.node_list)
                network.node_list[i].add_link(
                    network.node_list[wrap_index], distance_weights[x])

    # Special handling for \n node: remove all links to Punctuation objects
    for node in network.node_list:
        if node.name == '\n':
            node.link_list = [link for link in node.link_list if
                              link.target.name not in punctuation_list]

    # if self_links have been disabled,
    # remove all self referential links (except for blank lines)
    if not allow_self_links:
        for node in network.node_list:
            if node.name != '\n':
                node.remove_links_to_self()

    print('Word graph built with node list length of: {0}'.format(
        len(network.node_list)))
    return network

