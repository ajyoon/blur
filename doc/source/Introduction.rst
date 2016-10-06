Introduction
************

*blur* is a suite of tools for `Python <https://www.python.org/>`_ to help make
using chance operations in algorithmic art easier. ::

    >>> from blur.markov.graph import Graph
    >>> word_distance_weights = {-5: 1, -1: 2, 1: 8, 3: 3}
    >>> graph = Graph.from_string('blur is a suite of tools to help make using '
    ... 'chance operations in algorithmic art easier', word_distance_weights)
    >>> print(' '.join(graph.pick().value for i in range(10)))
    using chance algorithmic in algorithmic art easier blur easier blur

*blur* allows you to easily implement complex chance generated elements
in your works without getting bogged down in the boilerplate and the
nitty-gritty math. ::

    >>> from blur import soft, rand
    >>> frequency_profile = rand.normal_distribution(mean=440, variance=50)
    >>> for i in range(100):
    ...     add_oscillator(frequency=weighted_rand(frequency_profile))
    # -------------------------------------------------------------------------
    >>> color = soft.SoftColor(red=([(255, 10), (100, 0)],),
    ...                        green=([(200, 10), (100, 0)],),
    ...                        blue=([(0, 20), (80, 1)],))
    >>> apple.fill_color_rgb = color.get()
    # -------------------------------------------------------------------------
    >>> words = soft.SoftOptions([('nothing', 10),
    ...                           ('something', 3),
    ...                           ('everything', 1)])
    >>> print('I have {0} to say and I am saying it and that is poetry.'.format(
    ...     words.get())

At the heart of *blur* is the ``rand`` module, which contains a series of
functions for finding non-uniform random numbers based on customizable weights.
*blur* also comes with a model markov graph, a tool for deriving markov graphs
from text, a collection of soft objects whose values vary according to
customizable weights and rules, and a model I Ching.

Besides `Python <https://www.python.org/>`_ (version 2.7 or 3.x),
*blur* has no dependencies, making it easy to incorporate into your project.

To install *blur* use pip from the command line: ::

    $ pip install blur
