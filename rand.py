#!/usr/bin/env python3

import copy
import random
from warnings import warn


###############################################################################
#   Module error classes
###############################################################################
class PointNotFoundError(Exception):
    pass


###############################################################################
#   Local utility functions
###############################################################################
def _linear_interp(x1, y1, x2, y2, x3, round_result=False):
    """Take two points and interpolate between them at x3"""
    slope = (y2 - y1) / (x2 - x1)
    y_int = y1 - (slope * x1)
    result = (slope * x3) + y_int
    if round_result:
        return int(round(result))
    else:
        return result


def _point_under_curve(curve, point):
    """
    Determine if a point is under a piecewise curve defined by a list of points

    Points within ``curve`` must be sorted in nondecreasing order by x value.
    If multiple points in ``curve`` have the same x value, all but the last
    will be ignored.

    Args:
        curve [(x, y)]:
        point (x, y):

    Returns: Bool
    """
    for i in range(0, len(curve) - 1):
        # Skip over points which have the same x value
        # arbitrarily preferring the last occuring point with that x value
        if curve[i][0] == curve[i + 1][0]:
            continue
        if curve[i][0] <= point[0] <= curve[i + 1][0]:
            curve_y = _linear_interp(curve[i][0], curve[i][1],
                                     curve[i + 1][0], curve[i + 1][0],
                                     point[0])
            if point[1] < curve_y:
                # The sample point is under the curve
                return True
    else:
        return False


###############################################################################
# Methods
###############################################################################
def prob_bool(probability):
    """
    Return True or False depending on probability

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
    Return either positive or negative ``value`` based on ``prob_pos``

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
    Return either 1 with probability of ``prob_pos``, otherwise -1

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


def weighted_curve_rand(weights, round_result=False):
    """
    Generate a non-uniform random value based on a list of tuple weights

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
    while attempt_count < 50000:
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
        warn('Point not being found in weighted_curve_rand() after 50000 '
             'attempts, defaulting to a random weight point')
        return random.choice(weights)[0]


def weighted_option_rand(weights):
    """
    Generate a non-uniform random value based on a list of weight tuples.
    Treats each outcome as a discreet unit with a chance to occur.

    Constructs a line segment where each weight is outcome is allotted a
    length and rolls a random point.

    Weight tuples should be of the form: (outcome, weight). Weight
    outcome values may be of any type. Weights with weight 0 or less will have
    no chance to be rolled.

    Args:
        weights (list[(outcome, weight)]):

    Returns: Any

    Raises: PointNotFoundError
    """
    # If there's only one choice, choose it
    if len(weights) == 1:
        return weights[0][0]

    prob_sum = sum(w[1] for w in weights)
    sample = random.uniform(0, prob_sum)
    current_pos = 0
    i = 0
    while i < len(weights):
        if current_pos <= sample <= (current_pos + weights[i][1]):
            return weights[i][0]
        current_pos += weights[i][1]
        i += 1
    else:
        raise PointNotFoundError


def weighted_sort(weights):
    """

    Args:
        weights [(Any, float, float)]:
            [(list_item, place_in_percent, weight)]

    Returns: One of the objects in weights[][0]

    """
    # TODO: Build me
    pass
