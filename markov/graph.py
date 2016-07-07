
"""
UNDER RECONSTRUCTION - APOLOGIES FOR THE MESS
"""

from __future__ import division
import random


from chance.rand import weighted_option_rand
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

        TODO: Explain me better

        Args:
            factor (float): multiplier of neighbor links
            include_self (bool): if nodes can be feathered to themselves

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
        Pick a node in the graph based on node ``use_weight`` values.

        Additionally, set ``self.current_node`` to the newly picked node.

        Returns: Node
        """
        node = weighted_option_rand([(n.name, n.use_weight)
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
        # Use weighted_option_rand on start_node.link_list
        self.current_node = weighted_option_rand(
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

# TODO: Heavily rewrite me!!!
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
    node_sequence = []
    network = Graph()
    network.source = source

    # Set up relative position weights
    if distance_weights is None:
        distance_weights = {1: 1000, 2: 100, 3: 80, 4: 60, 5: 50,
                            6: 40, 7: 30, 8: 17, 9: 14, 10: 10,
                            11: 10, 12: 10, 13: 5, 14: 5, 15: 75}

    file_string = open(source).read()

    # Parse the file_string, sending words, and punctuations
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

    network.add_nodes(node_sequence, merge_same_words)
    # Find all relationships according to distance_weights
    for i in range(len(network.node_list)):
        for x in distance_weights.keys():
            # Make indexes circular to prevent IndexErrors
            index_sign = 1 if x >= 0 else -1
            wrapped_index = (x + i) % (index_sign * len(network.node_list))
            network.node_list[i].add_link(network.node_list[wrapped_index],
                                          distance_weights[x])

    # if self_links have been disabled,
    # remove all self referential links (except for blank lines)
    if not allow_self_links:
        for node in network.node_list:
            if node.name != '\n':
                node.remove_links_to_self()

    return network
