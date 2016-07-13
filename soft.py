# Make a series of classes for soft numbers
# whose values change every time they are retrieved
# according to defined chance profiles
#
# Could make subclasses for float, int, bool, maybe some others?
#
# Even a more complicated soft string could be defined

from warnings import warn

import random
import rand


class SoftObject:
    """
    An abstract base class for ``SoftObject``s.

    Every SoftObject represents a stochastic blurry object whose value
    is determined with the ``get()`` function.
    """
    def get(self):
        raise NotImplementedError

    # Needed?
    # def drift_weights(self):
    #    raise NotImplementedError


class SoftOptions(SoftObject):
    """
    One of many objects with optional varied weights
    """
    def __init__(self, options):
        """
        Initialize from a list of (value, weight) tuples

        Args:
            list[(value, weight)] options:
        """
        if not isinstance(options, list):
            if isinstance(options, tuple):
                if len(options) == 2:
                    self.options = [options]
                    return
                elif len(options) == 1:
                    self.options = [options[0], 1]
                    return
                else:
                    raise TypeError
            else:
                raise TypeError

        self.options = options

    @classmethod
    def with_uniform_weights(cls, options):
        """
        Initialize from a list of options, assigning uniform weights

        Args:
            options list[Any]:

        Returns: SoftOptions
        """
        return cls([(value, 1) for value in options])

    @classmethod
    def with_random_weights(cls, options, weight_profile=None):
        """
        Initialize from a list of options, assigning random weights which
        can optionally be themselves controlled by a list of weights

        Args:
            options list[Any]:
            weight_profile list[(number, number)]: a list of weights
                which will be used to determine the weights of the options

        Returns: SoftOptions
        """
        if weight_profile is None:
            return cls([((value, random.randint(1, 10)) for value in options)])
        else:
            return cls([(value,
                         rand.weighted_curve_rand(weight_profile, True))
                       for value in options])

    def get(self):
        return rand.weighted_option_rand(self.options)


class SoftFloat(SoftObject):
    """
    A stochastic float value defined by a list of weights
    """
    def __init__(self, weights):
        if not isinstance(weights, list):
            if isinstance(weights, tuple):
                if len(weights) > 2:
                    self.weights = [weights]
                    return
                elif len(weights) == 1:
                    self.weights = [weights[0], 1]
                    return
                else:
                    raise TypeError
            else:
                raise TypeError
        self.weights = weights

    @classmethod
    def bounded_uniform(cls, lowest, highest, weight_interval=None):
        """
        Initialize with a uniform distribution between a lowest and highest
        value.

        If no ``weight_interval`` is passed, this weight distribution
        will just consist of ``[(lowest, 1), (highest, 1)]``. If specified,
        weights (still with uniform weight distribution) will be added every
        ``weight_interval``. Use this if you intend to modify the weights
        in any complex way after initialization.

        Args:
            lowest (float or int):
            highest (float or int):
            weight_interval (int):

        Returns: SoftFloat
        """
        if weight_interval is None:
            weights = [(lowest, 1), (highest, 1)]
        else:
            i = lowest
            weights = []
            while i < highest:
                weights.append((i, 1))
                i += weight_interval
            weights.append((highest, 1))
        return cls(weights)

    def get(self):
        """
        Get a ``float`` value in the probability space of the object

        Returns: float
        """
        return rand.weighted_curve_rand(self.weights, round_result=False)


class SoftInt(SoftFloat):
    """
    A stochastic int value defined by a list of weights. Has the exact
    same functionality as SoftFloat, except that ``get()`` returns int values
    """
    def get(self):
        """
        Get an ``int`` value in the probability space of the object

        Returns: int
        """
        return rand.weighted_curve_rand(self.weights, round_result=True)


class SoftColor(SoftObject):
    """
    An RGB color whose individual channels are ``SoftInt`` objects

    ``SoftColor.get()`` returns an ``(r, g, b) tuple``.
    To get a hexadecimal color value, use ``to_hex()``.

    Examples:
        >>> color.get()
        (234, 124, 32)
        >>> color.get().to_hex()
        #ea7c20
    """
    def __init__(self, red, green, blue):
        """
        Args:
            red (SoftInt or tuple(args for SoftInt)):
            green (SoftInt or tuple(args for SoftInt)):
            blue (SoftInt or tuple(args for SoftInt)):
        """
        self.red = red
        if isinstance(red, tuple):
            self.red = SoftInt(*self.red)
        self.green = green
        if isinstance(green, tuple):
            self.green = SoftInt(*self.green)
        self.blue = blue
        if isinstance(blue, tuple):
            self.blue = SoftInt(*self.blue)

    @staticmethod
    def _bound_color_value(color):
        """
        Clamp a color value to be between ``0`` and ``255``

        Args:
            color (int):

        Returns: int
        """
        if color < 0:
            return 0
        elif color > 255:
            return 255
        else:
            return color

    @staticmethod
    def to_hex(color):
        """
        Convert a color tuple to a hexadecimal string

        Args:
            color (tuple):

        Returns: string
        """
        return '#{0:02x}{1:02x}{2:02x}'.format(
            _bound_color_value(color[0]),
            _bound_color_value(color[1]),
            _bound_color_value(color[2]))

    def get(self):
        """
        Get a color tuple
        """
        return (self.red.get(), self.green.get(), self.blue.get())
