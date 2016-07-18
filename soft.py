"""A collection of soft objects.

Every soft object has a value that changes every time it is retrieved
according to defined chance profiles. This value can be retrieved
with the ``SoftObject``'s``get()`` method.
"""

import random
from blur import rand


class SoftObject:
    """
    An abstract base class for ``SoftObject``s.

    Direct instances of ``SoftObject`` should not be created; instead, the
    appropriate subclass should be used.

    Every SoftObject represents a stochastic blurry object whose value
    is determined with the ``get()`` method.
    """

    def __init__(self):
        """
        Create a new ``SoftObject``.

        This is an abstract method and should not be called. Subclasses of
        ``SoftObject`` must override and implement this.

        Direct instances of ``SoftObject`` should not be created; instead, the
        appropriate subclass should be used.
        """
        raise NotImplementedError

    def get(self):
        """
        Retrieve a value of this ``SoftObject``.

        This is an abstract method and should not be called. Subclasses of
        ``SoftObject`` must override and implement this.
        """
        raise NotImplementedError


class SoftOptions(SoftObject):
    """One of many objects with corrosponding weights."""

    def __init__(self, options):
        """
        Initialize from a list of (value, weight) tuples.

        Args:
            list[(value, weight)] options:
        """
        self.options = options

    @classmethod
    def with_uniform_weights(cls, options, weight=1):
        """
        Initialize from a list of options, assigning uniform weights.

        Args:
            options list[Any]: The list of options this object can return
                with the ``get()`` method.
            weight (Optional[float or int]): The weight to be assigned to
                every option. Regardless of what this is, the probability
                of each option will be the same. In almost all cases this can
                be ignored. The only case for explicitly setting this is if
                you need to modify the weights after creation
                with specific requirements.

        Returns: SoftOptions
        """
        return cls([(value, weight) for value in options])

    @classmethod
    def with_random_weights(cls, options):
        """
        Initialize from a list of options with random weights.

        The weights assigned to each object are uniformally random
        integers between ``1`` and ``len(options)``

        Args:
            options list[Any]:

        Returns: SoftOptions
        """
        return cls(
            [(value, random.randint(1, len(options)))
             for value in options])

    def get(self):
        """
        Get one of the options within the probability space of the object.

        Returns: Any
        """
        return rand.weighted_choice(self.options)


class SoftBool(SoftObject):
    """A stochastic ``bool`` defined by a probability to be ``True``."""

    def __init__(self, prob_true):
        """
        Initialize from a probability to be ``True``.

        Args:
            prob_true (float): The probability that ``get()`` returns ``True``
                where ``prob_true <= 0`` is always ``False`` and
                ``prob_true >= 1`` is always ``True``.
        """
        self.prob_true = prob_true

    def get(self):
        """
        Get either ``True`` or ``False`` depending on ``self.prob_true``.

        Returns: bool
        """
        return random.uniform(0, 1) <= self.prob_true


class SoftFloat(SoftObject):
    """A stochastic float value defined by a list of weights."""

    def __init__(self, weights):
        """
        Initialize from a list of weights.

        Args:
            weights (list[tuple(float, float)])
        """
        self.weights = weights

    @classmethod
    def bounded_uniform(cls, lowest, highest, weight_interval=None):
        """
        Initialize with a uniform distribution between two values.

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
        Get a ``float`` value in the probability space of the object.

        Returns: float
        """
        return rand.weighted_rand(self.weights, round_result=False)


class SoftInt(SoftFloat):
    """
    A stochastic int value defined by a list of weights.

    Has the exact same functionality as SoftFloat,
    except that ``get()``returns int values
    """

    def get(self):
        """
        Get an ``int`` value in the probability space of the object.

        Returns: int
        """
        return rand.weighted_rand(self.weights, round_result=True)


class SoftColor(SoftObject):
    """
    An RGB color whose individual channels are ``SoftInt`` objects.

    ``SoftColor.get()`` returns an ``(r, g, b) tuple``.
    To get a hexadecimal color value, use ``to_hex()``.

    >>> rgb = color.get()
    >>> rgb
    (234, 124, 32)
    >>> rgb.to_hex()
    '#ea7c20'
    >>> color.get().to_hex()  # Pretending color.get() output is the same
    '#ea7c20'
    """

    def __init__(self, red, green, blue):
        """
        Initialize from soft values for rgb color channels.

        Args:
            red (SoftInt or tuple(args for SoftInt)):
            green (SoftInt or tuple(args for SoftInt)):
            blue (SoftInt or tuple(args for SoftInt)):
        """
        # TODO: Allow any of these values to be fixed int's as well
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
        Clamp a color value to be between ``0`` and ``255``.

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
        Convert a color tuple to a hexadecimal string.

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
        Get a color tuple.

        Returns: tuple(int, int, int)
        """
        return (self.red.get(), self.green.get(), self.blue.get())
