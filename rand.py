"""
A collection of functions for performing non-uniform random operations.

Many functions rely of weight tuples of the form ``(outcome, weight)``
"""

from __future__ import division
import copy
import random
import math

from warnings import warn


###############################################################################
#   Local utility functions
###############################################################################
def _linear_interp(curve, test_x, round_result=False):
    """
    Take a series of points and interpolate between them at ``test_x``.

    Args:
        curve (list[tuple]): A list of ``(x, y)`` points sorted in
            nondecreasing ``x`` value. If multiple points have the same
            ``x`` value, all but the last occuring will be ignored.
        test_x (float): The ``x`` value to find the ``y`` value of

    Raises:
        ValueError if ``test_x`` is out of the domain of ``curve``
    """
    index = 0
    for index in range(len(curve) - 1):
        # Ignore points which share an x value with the following point
        if curve[index][0] == curve[index + 1][0]:
            continue
        if curve[index][0] <= test_x <= curve[index + 1][0]:
            slope = ((curve[index + 1][1] - curve[index][1]) /
                     (curve[index + 1][0] - curve[index][0]))
            y_intercept = curve[index][1] - (slope * curve[index][0])
            result = (slope * test_x) + y_intercept
            if round_result:
                return int(round(result))
            else:
                return result
    else:
        raise ValueError


def _point_under_curve(curve, point):
    """
    Determine if a point is under a piecewise curve.

    Points within ``curve`` must be sorted in nondecreasing order by x value.
    If multiple points in ``curve`` have the same x value, all but the last
    will be ignored.

    Args:
        curve [(x, y)]:
        point (x, y):

    Returns: bool
    """
    try:
        return _linear_interp(curve, point[0]) > point[1]
    except ValueError:
        return False


def _clamp_value(value, minimum, maximum):
    """
    Clamp a value to fit between a minimum and a maximum.

    * If ``value`` is between ``minimum`` and ``maximum``, return ``value``
    * If ``value`` is below ``minimum``, return ``minimum``
    * If ``value is above ``maximum``, return ``maximum``

    Args:
        value (float or int): The number to clamp
        minimum (float or int): The lowest allowed return value
        maximum (float or int): The highest allowed return value

    Returns:
        float or int: the clamped value

    Raises:
        ValueError: if maximum < minimum
    """
    if maximum < minimum:
        raise ValueError
    if value < minimum:
        return minimum
    elif value > maximum:
        return maximum
    else:
        return value


###############################################################################
# Methods
###############################################################################
def bound_weights(weights, minimum=None, maximum=None):
    """
    Bound a weight list so that all outcomes fit within specified bounds.

    The probability distribution within the minimum and maximum values remains
    the same. Weights in the list with outcomes outside of ``minimum`` and
    ``maximum`` are removed. If weights are removed from either end, attach
    weights at the modified edges at the same weight (y-axis) position they
    had interpolated in the original list.

    At least one of ``minimum`` and ``maximum`` must be set,
    or else this raises TypeError

    Args:
        weights (list[(float or int, float or int)]): the list of weights
            to be bounded. Must be sorted in increasing order of outcomes
        minimum (float or int): Lowest allowed outcome for the weight list
        maximum (float or int) Highest allowed outcome for the weight list

    Returns:
        list[(int or float, int or float)]: The bounded weight list

    Raises:
        ValueError: if ``maximum < minimum``
        TypeError: if both ``minimum`` and ``maximum`` are ``None``
    """
    # Copy weights to avoid side-effects
    bounded_weights = weights[:]
    # Remove weights outside of minimum and maximum
    if minimum is not None and maximum is not None:
        if maximum < minimum:
            raise ValueError
        bounded_weights = [bw for bw in bounded_weights
                           if minimum <= bw[0] <= maximum]
    elif minimum is not None:
        bounded_weights = [bw for bw in bounded_weights
                           if minimum <= bw[0]]
    elif maximum is not None:
        bounded_weights = [bw for bw in bounded_weights
                           if bw[0] <= maximum]
    else:
        # Both minimum and maximum are not defined
        raise TypeError
    # If weights were removed, attach new endpoints where they would have
    # appeared in the original curve
    if (bounded_weights[0][0] > weights[0][0] and
            bounded_weights[0][0] != minimum):
        bounded_weights.insert(0, (minimum, _linear_interp(weights, minimum)))
    if (bounded_weights[-1][0] < weights[-1][0] and
            bounded_weights[-1][0] != maximum):
        bounded_weights.append((maximum, _linear_interp(weights, maximum)))
    return bounded_weights


def normal_distribution(mean, variance,
                        minimum=None, maximum=None, weight_count=23):
    """
    Return a list of weights approximating a normal distribution.

    Args:
        mean (float): The mean of the distribution
        variance (float): The variance of the distribution
        minimum (float): The minimum outcome possible to
            bound the output distribution to
        maximum (float): The maximum outcome possible to
            bound the output distribution to
        weight_count (Optional[int]): The number of weights that will
            be used to approximate the distribution

    Returns: list[(float, float)]

    Raises:
        ValueError: if ``maximum < minimum``
        TypeError: if both ``minimum`` and ``maximum`` are ``None``
    """
    def _normal_function(x, mean, variance):
        e_power = -1 * (((x - mean) ** 2) / (2 * variance))
        return (1 / math.sqrt(2 * variance * math.pi)) * (math.e ** e_power)
    # Pin 0 to +- 5 sigma as bounds, or minimum and maximum
    # if they cross +/- sigma
    standard_deviation = math.sqrt(variance)
    min_x = (standard_deviation * -5) + mean
    max_x = (standard_deviation * 5) + mean
    step = (max_x - min_x) / weight_count
    current_x = min_x
    weights = []
    while current_x < max_x:
        weights.append((current_x,
                        _normal_function(current_x, mean, variance)))
        current_x += step
    if minimum is not None or maximum is not None:
        return bound_weights(weights, minimum, maximum)
    else:
        return weights


def prob_bool(probability):
    """
    Return True or False depending on probability.

    Args:
        probability (float): Probability (between 0 and 1) to return True

    Returns: Bool
    """
    return random.uniform(0, 1) < probability


def percent_possible(percent):
    """
    Return True ``percent`` / 100 times.

    Args:
        percent (int or float): percent possibility to return True

    Returns: Bool
    """
    return random.uniform(0, 100) < percent


def pos_or_neg(value, prob_pos=None):
    """
    Return either positive or negative ``value`` based on ``prob_pos``.

    A convenience function for ``abs(value) * pos_or_neg_1``

    Args:
        value (int or float): the value to operate on
        prob_pos (Optional[float]): The probability to return positive.
            Should be between 0 and 1. If not specified, assume 0.5

    Returns: int or float
    """
    return abs(value) * pos_or_neg_1(prob_pos)


def pos_or_neg_1(prob_pos=None):
    """
    Return either 1 with probability of ``prob_pos``, otherwise -1.

    Args:
        prob_pos (Optional[float]): The probability to return (+)1.
            Should be between 0 and 1. If not specified, assume 0.5

    Returns: int, either 1 or -1
    """
    if prob_pos is None:
        prob_pos = 0.5
    if random.uniform(0, 1) < prob_pos:
        return 1
    else:
        return -1


def weighted_rand(weights, round_result=False):
    """
    Generate a non-uniform random value based on a list of tuple weights.

    Treats weights as coordinates for a probability distribution curve and
    rolls accordingly. Constructs a piece-wise linear curve according to
    coordinates given in input_weights and rolls random values in the
    curve's bounding box until a value is found under the curve

    Weight tuples should be of the form: (outcome, weight). All weights
    outcome values must be numbers. Weights with weight 0 or less will have
    no chance to be rolled

    Args:
        weights (list[(outcome, weight)]):
        round_result (Optional[Bool])):

    Returns: float or int
    """
    # If just one weight is passed, simply return the weight's name
    if len(weights) == 1:
        return weights[0][0]

    # Is there a way to do this more efficiently? Maybe even require that
    # ``weights`` already be sorted?
    weights = sorted(weights, key=lambda w: w[0])

    x_min = weights[0][0]
    x_max = weights[-1][0]
    y_min = 0
    y_max = max([point[1] for point in weights])

    # Roll random numbers until a valid one is found
    attempt_count = 0
    while attempt_count < 500000:
        # Get sample point
        sample = (random.uniform(x_min, x_max), random.uniform(y_min, y_max))
        if _point_under_curve(weights, sample):
            # The sample point is under the curve
            if round_result:
                return int(round(sample[0]))
            else:
                return sample[0]
        attempt_count += 1
    else:
        warn('Point not being found in weighted_rand() after 500000 '
             'attempts, defaulting to a random weight point. '
             'If this happens often, it is probably a bug, so please let us '
             'know with a bug report at https://github.com/ajyoon/blur')
        return random.choice(weights)[0]


def weighted_choice(weights):
    """
    Generate a non-uniform random value based on a list of weight tuples.

    Treats each outcome as a discreet unit with a chance to occur.

    Constructs a line segment where each weight is outcome is allotted a
    length and rolls a random point.

    Weight tuples should be of the form: (outcome, weight). Weight
    outcome values may be of any type. Weights with weight 0 or less will have
    no chance to be rolled, unless all weights are 0, in which case a
    uniformally random choice will be returned.

    Args:
        weights (list[(outcome, weight)]):

    Returns: Any
    """
    # If there's only one choice, choose it
    if len(weights) == 1:
        return weights[0][0]
    # Remove all weights with weight 0 or less
    working_weights = [w for w in weights if w[1] > 0]
    # If no weights remain after trimming, choose a random option
    if not working_weights:
        return random.choice([w[0] for w in weights])
    # Construct a line segment where each weight outcome is
    # allotted a length equal to the outcome's weight,
    # pick a uniformally random point along the line, and take
    # the outcome that point corrosponds to
    prob_sum = sum(w[1] for w in working_weights)
    sample = random.uniform(0, prob_sum)
    current_pos = 0
    i = 0
    while i < len(working_weights):
        if current_pos <= sample <= (current_pos + working_weights[i][1]):
            return working_weights[i][0]
        current_pos += working_weights[i][1]
        i += 1
    else:
        warn("Option couldn't be found in weighted_choice(). "
             "It's not you it's me. "
             "Please submit a bug report at https://github.com/ajyoon/blur")
        return random.choice([opt[0] for opt in options])


def weighted_shuffle(weights):
    """
    Non-uniformally shuffle a list.

    ``weights`` is a list of the form: [(list_item, place, weight)].
    ``list_item`` is the item to place in the final list. ``place`` is either a
    ``float`` between 0 and 100 representing the percent along the list it will
    end up, or the ``str`` 'STAY' meaning the item will stay where it appears
    in ``weights``. ``weight`` is the weight given to the chance that the item
    appears in the specified ``place``.

    The algorithm works by choosing an item from ``weights`` according to the
    ``weight`` element and placing its ``list_item`` its the specified
    ``place``. Items with the lowest ``weight`` will tend to be placed last,
    filling in gaps left between higher priority items, making their positions
    less predictable. ``weight`` values of 0 have the lowest possible
    priority and will be placed anywhere left after other items have been
    placed.

    Args:
        weights [(Any, float or str, float)]:

    Returns:
        list: The shuffled list

    Raises:
        ValueError: If passed ``weights`` is not formed correctly
    """
    working_list = weights[:]
    # list of tuples [list_item, target_index]
    # used to store positions before moving them into the final list
    shuffle_positions = []

    def closest_available(requested_index):
        """The closest index that isn't taken in ``shuffle_positions``."""
        taken_positions = [position[1] for position in shuffle_positions]
        available_indexes = [i for i in range(len(weights))
                             if i not in taken_positions]
        return min((available_index for available_index in available_indexes),
                   key=lambda index: abs(move_index - index))

    while working_list:
        # Pick which item to move
        move_index = weighted_choice(
            [(index, weight[2]) for index, weight in enumerate(working_list)])
        move_item = working_list[move_index][0]
        # Find the index where the item will be placed
        if isinstance(working_list[move_index][1], str):
            if working_list[move_index][1] == 'STAY':
                # Place in the index closest to where the item appears already
                target_position = closest_available(move_index)
            else:
                raise ValueError
        else:
            # Place in the index closest to working_list[][1] percent along
            requested_index = int((working_list[move_index][1] / 100) *
                                  move_index)
            target_position = closest_available(requested_index)
        shuffle_positions.append((move_item, target_position))
        # Remove the item weight from working_list
        working_list.pop(move_index)

    # Construct the shuffled list and return it
    shuffled_list = [None] * len(weights)
    for item, target_index in shuffle_positions:
        shuffled_list[target_index] = item
    return shuffled_list
