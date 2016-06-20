#!/usr/bin/env python

from .network import Network
from .nodes import Value, WeightListNode


def indenter():
    """
    Builds and returns a network which controls behavior for indentation values (either left- or right- indentation)
    :return: instance of chance.network.Network
    """

    network = Network()

    n1 = Value(0)
    n2 = WeightListNode('Shift Right', [(1, 20), (3, 3), (11, 1)])
    n3 = WeightListNode('Shift Left', [(-1, 20), (-3, 3), (-11, 1)])
    n4 = WeightListNode('Jump Right', [(14, 5), (85, 25), (110, 1), (170, 10)])
    n5 = WeightListNode('Jump Left', [(-14, 5), (-85, 25), (-110, 1), (-170, 10)])

    n1.add_link(n1, 40)
    n1.add_link(n2, 3)
    n1.add_link(n3, 3)
    n1.add_link(n4, 10)
    n1.add_link(n5, 10)

    n2.add_link(n1, 60)
    n2.add_link(n2, 100)
    n2.add_link(n3, 50)
    n2.add_link(n4, 10)
    n2.add_link(n5, 10)

    n3.add_link(n1, 60)
    n3.add_link(n2, 30)
    n3.add_link(n3, 100)
    n3.add_link(n4, 20)

    n4.add_link(n1, 10)

    n5.add_link(n1, 30)
    network.add_nodes([n1, n2, n3, n4, n5])
    return network


def indenter_erratic():
    """
    Does the same thing as indenter() but with a stronger bias toward jumping left and right.
    Builds and returns a network which controls behavior for indentation values (either left- or right- indentation)
    :return: instance of chance.network.Network
    """

    network = Network()

    n1 = Value(0)
    n2 = WeightListNode('Shift Right', [(3, 6), (11, 1)])
    n3 = WeightListNode('Shift Left', [(-3, 6), (-11, 1)])
    n4 = WeightListNode('Jump Right', [(14, 0), (85, 20), (110, 1), (170, 10)])
    n5 = WeightListNode('Jump Left', [(-14, 0), (-85, 20), (-110, 1), (-170, 10)])

    n1.add_link(n1, 40)
    n1.add_link(n2, 3)
    n1.add_link(n3, 3)
    n1.add_link(n4, 30)
    n1.add_link(n5, 30)
    n2.add_link(n1, 60)
    n2.add_link(n2, 100)
    n2.add_link(n3, 50)
    n3.add_link(n1, 60)
    n3.add_link(n3, 100)
    n3.add_link(n2, 30)
    n3.add_link(n4, 20)
    n4.add_link(n1, 10)
    n5.add_link(n1, 30)
    network.add_nodes([n1, n2, n3, n4, n5])
    return network


def instrument_indenter():
    """
    Builds and returns a network which controls behavior for indentation values (either left- or right- indentation)
    Network values specialized for instrument indentation
    :return: instance of chance.network.Network
    """

    network = Network()
    n1 = Value(0)
    n2 = WeightListNode('Shift Right', [(3, 6), (11, 1)])
    n3 = WeightListNode('Shift Left', [(-3, 6), (-11, 1)])
    n4 = WeightListNode('Jump Right', [(14, 0), (85, 20), (110, 1), (170, 10)])
    n5 = WeightListNode('Jump Left', [(-14, 0), (-85, 20), (-110, 1), (-170, 10)])

    n1.add_link(n1, 70)
    n1.add_link(n2, 3)
    n1.add_link(n3, 3)
    n1.add_link(n4, 20)
    n1.add_link(n5, 20)

    n2.add_link(n1, 60)
    n2.add_link(n2, 100)
    n2.add_link(n3, 50)
    n2.add_link(n5, 60)

    n3.add_link(n1, 60)
    n3.add_link(n3, 100)
    n3.add_link(n2, 30)
    n3.add_link(n4, 20)

    n4.add_link(n1, 10)

    n5.add_link(n1, 30)

    network.add_nodes([n1, n2, n3, n4, n5])
    return network


def instrument_pause_or_play():
    """
    Constructs and returns a network with two states: 1 (play) and 0 (don't play)
    Designed so that, when passed to document_tools.pdf_scribe, 'don't play' results in a space equal to the
    global font size (shared.Globals.FontSize)
    :return: instance of chance.network.Network
    """
    network = Network()
    dense_play = Value(1)
    play = Value(1)
    light_play = Value(1)
    light_rest = Value(0)
    rest = Value(0)
    dense_rest = Value(0)

    dense_play.add_link(dense_play, 40)
    dense_play.add_link(light_play, 1)
    dense_play.add_link(dense_rest, 2)

    play.add_link(dense_play, 2)
    play.add_link(play, 10)
    play.add_link(light_play, 4)
    play.add_link(light_rest, 5)
    play.add_link(rest, 4)

    light_play.add_link(play, 2)
    light_play.add_link(light_rest, 4)

    light_rest.add_link(rest, 3)
    light_rest.add_link(dense_rest, 1)
    light_rest.add_link(light_rest, 2)
    light_rest.add_link(light_play, 2)

    rest.add_link(rest, 4)
    rest.add_link(dense_rest, 3)
    rest.add_link(light_play, 1)

    dense_rest.add_link(dense_rest, 14)
    dense_rest.add_link(rest, 2)
    dense_rest.add_link(light_play, 1)

    network.add_nodes([dense_play, play, light_play, light_rest, rest, dense_rest])
    return network


def music_rhythmic_or_not():
    """
    Constructs and returns a network with two states: True (rhythmic) and False (non-rhythmic)
    Designed with a strong bias toward non-rhythmic content
    :return: instance of chance.network.Network
    """
    network = Network()
    dense_rhythmic = Value(True)
    rhythmic = Value(True)
    first_rhythmic = Value(True)
    non_rhythmic = Value(False)
    dense_non_rhythmic = Value(False)
    
    dense_rhythmic.add_link(dense_rhythmic, 15)
    dense_rhythmic.add_link(non_rhythmic, 1)

    rhythmic.add_link(dense_rhythmic, 1)
    rhythmic.add_link(rhythmic, 5)
    rhythmic.add_link(non_rhythmic, 5)

    # Because it's not meaningful to have just one rhythmic note surrounded by non-rhythmic ones,
    # Make absolutely sure that all rhythmic notes are followed by at least one other
    first_rhythmic.add_link(rhythmic, 3)
    first_rhythmic.add_link(dense_rhythmic, 1)

    non_rhythmic.add_link(non_rhythmic, 10)
    non_rhythmic.add_link(dense_non_rhythmic, 1)
    non_rhythmic.add_link(first_rhythmic, 3)

    dense_non_rhythmic.add_link(dense_non_rhythmic, 10)
    dense_non_rhythmic.add_link(non_rhythmic, 1)
    dense_non_rhythmic.add_link(first_rhythmic, 1)

    network.add_nodes([dense_rhythmic, rhythmic, first_rhythmic, non_rhythmic, dense_non_rhythmic])
    return network


def rhythm():
    """
    Constructs and returns a network which outputs floating point numbers between -1 and 1
    :return: instance of chance.network.Network
    """
    network = Network()

    stay_same = Value(0)
    much_slower = WeightListNode('Major Slower', [(-1, 1), (-0.5, 3), (-0.2, 10)])
    slightly_slower = WeightListNode('Slight Slower', [(-0.2, 1), (-0.01, 10)])
    slightly_faster = WeightListNode('Slight Faster', [(1, 1), (0.5, 3), (0.2, 10)])
    much_faster = WeightListNode('Major Faster', [(0.2, 1), (0.01, 10)])
    
    stay_same.add_link(stay_same, 40)
    stay_same.add_link(much_slower, 3)
    stay_same.add_link(slightly_slower, 3)
    stay_same.add_link(slightly_faster, 30)
    stay_same.add_link(much_faster, 30)
    much_slower.add_link(stay_same, 60)
    much_slower.add_link(much_slower, 100)
    much_slower.add_link(slightly_slower, 50)
    slightly_slower.add_link(stay_same, 60)
    slightly_slower.add_link(slightly_slower, 100)
    slightly_slower.add_link(much_slower, 30)
    slightly_slower.add_link(slightly_faster, 20)
    slightly_faster.add_link(stay_same, 10)
    much_faster.add_link(stay_same, 30)

    network.add_nodes([stay_same, much_slower, slightly_slower, slightly_faster, much_faster])
    return network

def text_pause_or_write():
    """
    Constructs and returns a network with two states: 1 (write) and 0 (don't write)
    Designed so that, when passed to document_tools.pdf_scribe, 'don't write' results in a space equal to the
    global font size (shared.Globals.FontSize)
    :return: instance of chance.network.Network
    """
    network = Network()
    dense_write = Value(1)
    write = Value(1)
    light_write = Value(1)
    light_rest = Value(0)
    rest = Value(0)
    dense_rest = Value(0)

    dense_write.add_link(dense_write, 1000)
    dense_write.add_link(light_write, 15)
    dense_write.add_link(light_rest, 1)

    write.add_link(dense_write, 1)
    write.add_link(write, 50)
    write.add_link(light_write, 4)
    write.add_link(light_rest, 12)

    light_write.add_link(write, 4)
    light_write.add_link(light_write, 10)
    light_write.add_link(light_rest, 8)

    light_rest.add_link(dense_rest, 1)
    light_rest.add_link(light_rest, 5)
    light_rest.add_link(light_write, 14)

    rest.add_link(rest, 5)
    rest.add_link(dense_rest, 6)
    rest.add_link(light_write, 30)

    dense_rest.add_link(dense_rest, 30)
    dense_rest.add_link(rest, 2)
    dense_rest.add_link(light_write, 2)

    network.add_nodes([dense_write, write, light_write, light_rest, rest, dense_rest])
    return network
