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
    Args:
        curve [(x, y)]:
        point (x, y):

    Returns: Bool
    """
    for i in range(0, len(curve) - 1):
        if curve[i][0] <= point[0] <= curve[i + 1][0]:
            curve_y = _linear_interp(curve[i][0], curve[i][1],
                                     curve[i + 1][0], curve[i + 1][0],
                                     point[0])
            if point[1] <= curve_y:
                # The sample point is under the curve
                return True
    else:
        return False


###############################################################################
#   Weight class
###############################################################################
class Weight:
    def __init__(self, outcome, weight):
        self.x = outcome
        self.y = weight


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


def pos_or_neg(value, pos_weight=None, neg_weight=None):
    """
    Return either positive or negative ``value``

    If both ``pos_weight`` and ``neg_weight`` are numbers, use them as
    weights to decide the outcome. Otherwise flip a coin. This is a convenience
    function for ``some_val = abs(some_val) * pos_or_neg_1()``

    Args:
        value (int or float): the value to operate on
        pos_weight (int or float): weight to return 1
        neg_weight (int or float): weight to return -1

    Returns: int or float
    """
    return abs(value) * pos_or_neg_1(pos_weight, neg_weight)
    

def pos_or_neg_1(pos_weight=None, neg_weight=None):
    """
    Return either 1 or -1

    If both ``pos_weight`` and ``neg_weight`` are numbers, use them as
    weights to decide the outcome. Otherwise flip a coin.

    Args:
        pos_weight (int or float): weight to return 1
        neg_weight (int or float): weight to return -1

    Returns: int (1 or -1)
    """
    if pos_weight is not None and neg_weight is not None:
        return weighted_option_rand([(1, pos_weight), (-1, neg_weight)])
    else:
        if random.randint(0, 1):
            return 1
        else:
            return -1


def markov_weights_dict(min_key, max_key):
    """
    Generate a dictionary of {distance, weight} pairs for use in
    network.word_mine()
    """
    pairs = random_weight_list(min_key, max_key, 1)
    return dict((weight.x, weight.y) for weight in pairs)


# TODO: Test me!
def merge_markov_weights_dicts(dict_1, dict_2, ratio):
    """Merge two markov_weights_dict's
    where ratio the weight of dict_1 to dict_2.
    Ratio must be greater than 0 and less than or equal to 1"""
    min_key = min(list(dict_1.keys()) + list(dict_2.keys()))
    max_key = max(list(dict_1.keys()) + list(dict_2.keys()))

    def interp_dict(in_dict):
        """Return a copy of in_dict with interpolated values for every
        integer key within the range of in_dict's keys"""
        out_dict = {}
        min_key = min(list(in_dict.keys()))
        max_key = max(list(in_dict.keys()))
        for key in range(min_key, max_key):
            if key in in_dict:
                out_dict[key] = in_dict[key]
            else:
                # We need to interpolate this key in out_dict
                # Find the nearest key to the left and right
                # (because the min and max keys are defined,
                # we have no edge case to deal with)
                lower_key = max([k for k in in_dict.keys() if k < key])
                lower_value = in_dict[lower_key]
                higher_key = min([k for k in in_dict.keys() if k > key])
                higher_value = in_dict[lower_key]
                out_dict[key] = _linear_interp(lower_key, lower_value,
                                               higher_key, higher_value,
                                               key)
        return out_dict

    interp_dict_1 = interp_dict(dict_1)
    interp_dict_2 = interp_dict(dict_2)
    # Merge the two dicts
    merged_dict = {}
    for key in range(min_key, max_key):
        if key in interp_dict_1 and key not in interp_dict_2:
            merged_dict[key] = interp_dict_1[key]
        elif key in interp_dict_2 and key not in interp_dict_1:
            merged_dict[key] = interp_dict_2[key]
        else:
            # Merge the values
            # If KeyError occurs, fix something above
            # There is probably some 4th grade algebra way to simplify this
            weighted_value = ((interp_dict_1[key] * ratio) +
                              (interp_dict_2[key] * (1 / ratio))) / 2
            merged_dict[key] = weighted_value

    return merged_dict


def weighted_curve_rand(weights, round_result=False):
    """
    Generate a non-uniform random value based on a list of input_weights or
    tuples. Treats input_weights as coordinates for a probability
    distribution curve and rolls accordingly. Constructs a piece-wise linear
    curve according to coordinates given in input_weights and rolls random
    values in the curve's bounding box until a value is found under the curve
    All input_weights outcome values must be numbers.

    Args:
        weights [(outcome, weight)]:
        round_result (Bool):

    Returns: float or int
    """
    # Type safety check
    if not isinstance(weights, list):
        weights = [weights]
    # TODO: Is it really necessary to copy the weights?
    weights = weights[:]
    i = 0
    while i < len(weights):
        if isinstance(weights[i], Weight):
            pass
        elif isinstance(weights[i], tuple):
            weights[i] = Weight(weights[i][0], weights[i][1])
        else:
            raise TypeError(
                "Weight at index {0} is not a valid type".format(str(i)))
        i += 1

    # TODO: Sort through all weight objects,
    # averaging the y value of objects with the same x
    """
    cleaned_weights = []
    for index in range(0, len(weights)):
        for test_index in range(0, len(weights)):
            if index == test_index:
                continue
            if weights[index].x == weights[test_index].x:
                mean_y = (weights[index].y + weights[test_index].y) / 2.0
                cleaned_weights.append((weights[index].x, mean_y))
    """

    # If just one weight is passed, simply return the weight's name
    if len(weights) == 1:
        return weights[0].x

    # Sort list so that weights are listed in order of ascending X value
    weights = sorted(weights, key=lambda w: w.x)

    x_min = weights[0].x
    x_max = weights[-1].x
    y_min = min([point.y for point in weights])
    y_max = max([point.y for point in weights])
    # Roll random numbers until a valid one is found
    attempt_count = 0
    while True:
        # Get sample point
        sample = (random.uniform(x_min, x_max), random.uniform(y_min, y_max))
        if _point_under_curve([(w.x, w.y) for w in weights], sample):
            # The sample point is under the curve
            if round_result:
                return int(round(sample[0]))
            else:
                return sample[0]
        attempt_count += 1
        if attempt_count > 10000:
            warn('Point not being found in weighted_curve_rand() after 10000 '
                 'attempts, defaulting to a random weight point')
            return random.choice(weights).x


def weighted_option_rand(weights):
    """
    Generate a non-uniform random value based on a list of input_weights or
    tuples. treats each outcome (Weight.x) as a discreet unit with a chance
    to occur. Constructs a line segment where each weight is outcome is
    allotted a length and rolls a random point. input_weights outcomes may be
    of any type, including instances

    Args:
        input_weights [(outcome, weight)]:

    Returns: a random name based on the weights
    """
    # Type safety check
    if not isinstance(weights, list):
        weights = [weights]
    # TODO: Is it really necessary to copy the weights?
    weights = weights[:]
    i = 0
    while i < len(weights):
        if isinstance(weights[i], Weight):
            pass
        elif isinstance(weights[i], tuple):
            weights[i] = Weight(weights[i][0], weights[i][1])
        else:
            raise TypeError(
                    "Weight at index {0} is not a valid type".format(str(i)))
        i += 1

    # If there's only one choice, choose it
    if len(weights) == 1:
        return weights[0].x

    prob_sum = sum(w.y for w in weights)
    sample = random.uniform(0, prob_sum)
    current_pos = 0
    i = 0
    while i < len(weights):
        if current_pos <= sample <= (current_pos + weights[i].y):
            return weights[i].x
        current_pos += weights[i].y
        i += 1
    else:
        raise PointNotFoundError


def random_weight_list(min_outcome, max_outcome, max_weight_density=0.1,
                       max_possible_weights=None):
    """
    Generate a list of Weight within a given min_outcome and max_outcome bound.

    Args:
        min_outcome (int or float):
        max_outcome (int or float):
        max_weight_density (float):  the maximum density of resulting weights
        max_possible_weights (int):

    Returns: [Weight]
    """

    # TODO: get rid of max_weight_density, its use is confusing and redundant

    # Prevent sneaky errors
    # Add resolution multiplier if either min_outcome or max_outcome are floats
    resolution_multiplier = None
    if ((not isinstance(min_outcome, int)) or
            (not isinstance(max_outcome, int))):
        resolution_multiplier = 1000.0
        min_outcome = int(round(min_outcome * resolution_multiplier))
        max_outcome = int(round(max_outcome * resolution_multiplier))
    if min_outcome > max_outcome:
        swapper = min_outcome
        min_outcome = max_outcome
        max_outcome = swapper

    # Set max_weights according to max_weight_density
    max_weights = int(round((max_outcome - min_outcome) * max_weight_density))

    if (max_possible_weights is not None) and (
            max_weights > max_possible_weights):
        max_weights = max_possible_weights

    # Create and populate weight_list

    # TODO: is there a better way?
    # Pin down random weights at min_outcome and max_outcome to keep the
    # weight_list properly bounded
    weight_list = [Weight(min_outcome, random.randint(1, 100)),
                   Weight(max_outcome, random.randint(1, 100))]

    # Main population loop. Subtract 2 from max_weights to account for
    # already inserted start and end caps
    for i in range(0, max_weights - 2):
        outcome = random.randint(min_outcome, max_outcome)
        is_duplicate_outcome = False
        # Test contents in weight_list to make sure
        # none of them have the same outcome
        for index in range(0, len(weight_list)):
            if weight_list[index].x == outcome:
                is_duplicate_outcome = True
                break
        if not is_duplicate_outcome:
            weight_list.append(Weight(outcome, random.randint(1, 100)))

    # Sort the list
    weight_list = sorted(weight_list, key=lambda z: z.x)

    # Undo resolution multiplication if necessary
    if resolution_multiplier is not None:
        resolved_weight_list = []
        for old_weight in weight_list:
            resolved_weight_list.append(Weight(
                round((old_weight.x / resolution_multiplier), 3),
                old_weight.y))
        weight_list = resolved_weight_list

    return weight_list


def weighted_sort(weights):
    """

    Args:
        weights [(Any, float, float)]:
            [(list_item, place_in_percent, weight)]

    Returns:

    """
    # TODO: Build me
    pass
