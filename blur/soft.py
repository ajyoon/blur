"""A collection of soft objects.

Every soft object has a value that changes every time it is retrieved
according to defined chance profiles. This value can be retrieved
with the ``SoftObject`` 's ``get()`` method.

>>> blurry_float = SoftFloat([(-1, 2), (3, 5)])
>>> blurry_float.get()
1.925674784815838
>>> blurry_float.get()
1.120389067727415
>>> blurry_float.get()
1.30418962132812
"""

import random
from blur import rand


class SoftObject:
    """
    An abstract base class for ``SoftObject`` 's.

    Direct instances of ``SoftObject`` should not be created; instead, the
    appropriate subclass should be used.

    Every SoftObject represents a stochastic blurry object whose value
    is determined with the ``get()`` method.
    """

    def __init__(self):
        """
        Initialize a ``SoftObject``.

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
    """
    One of many objects with corrosponding weights.

    Attributes:
        options (list): a list of options where each option
            is a ``tuple`` of form ``(Any, float)`` corresponding to
            ``(outcome, weight)``. Outcome values may be of any type.
            Weights ``0`` or less will have no chance
            to be retrieved by ``get()``
    """

    def __init__(self, options):
        """
        Initialize from a list of (outcome, weight) tuples.

        Args:
            options (list[tuple]): a list of options where each option
                is a ``tuple`` of form ``(Any, float)`` corresponding to
                ``(outcome, weight)``. Outcome values may be of any
                type. Weights ``0`` or less will have no chance
                to be retrieved by ``get()``
        """
        self.options = options

    @classmethod
    def with_uniform_weights(cls, options, weight=1):
        """
        Initialize from a list of options, assigning uniform weights.

        Args:
            options (List[Any]): The list of options this object can return
                with the ``get()`` method.
            weight (Optional[float or int]): The weight to be assigned to
                every option. Regardless of what this is, the probability
                of each option will be the same. In almost all cases this can
                be ignored. The only case for explicitly setting this is if
                you need to modify the weights after creation
                with specific requirements.

        Returns:
            SoftOptions: A newly constructed instance
        """
        return cls([(value, weight) for value in options])

    @classmethod
    def with_random_weights(cls, options):
        """
        Initialize from a list of options with random weights.

        The weights assigned to each object are uniformally random
        integers between ``1`` and ``len(options)``

        Args:
            options (list[Any]):

        Returns:
            SoftOptions: A newly constructed instance
        """
        return cls([(value, random.randint(1, len(options)))
                    for value in options])

    def get(self):
        """
        Get one of the options within the probability space of the object.

        Returns:
            Any: An item from ``self.options``.
        """
        return rand.weighted_choice(self.options)


class SoftBool(SoftObject):
    """
    A stochastic ``bool`` defined by a probability to be ``True``.

    Attributes:
        prob_true (float): The probability that ``get()`` returns ``True``
            where ``prob_true <= 0`` is always ``False`` and
            ``prob_true >= 1`` is always ``True``.
    """

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

        Returns:
            bool: ``True`` or ``False`` depending on ``self.prob_true``.
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

        Returns:
            SoftFloat: A newly constructed instance.
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

        Returns:
            float: A value between the lowest and highest outcomes
                in ``self.weights``
        """
        return rand.weighted_rand(self.weights, round_result=False)


class SoftInt(SoftFloat):
    """
    A stochastic ``int`` value defined by a list of weights.

    Has the exact same functionality as ``SoftFloat``,
    except that ``get()`` returns ``int`` values
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

    ``SoftColor.get()`` returns an ``(r, g, b)`` ``tuple``.
    To get a hexadecimal color value, use ``get_as_hex()``.

    >>> rgb = some_soft_color.get()
    >>> rgb
    (234, 124, 32)
    >>> SoftColor.rgb_to_hex(rgb)
    '#EA7C20'
    >>> some_soft_color.get_as_hex()  # Pretending output is the same rgb color
    '#EA7C20'
    """

    def __init__(self, red, green, blue):
        """
        Initialize from soft values for rgb color channels.

        Args:
            red (int or SoftInt or tuple(args for SoftInt)):
            green (int or SoftInt or tuple(args for SoftInt)):
            blue (int or SoftInt or tuple(args for SoftInt)):

        Notes:
            When initializing the soft color channels using the
            convenience option to pass a tuple of args for
            for ``SoftInt.__init__()``, keep in mind that when
            creating 1-length tuples in Python you need to add a
            comma after the first element, or Python will ignore
            the parentheses. ::

                color = soft.SoftColor(([(0, 1), (255, 10)],),
                                       ([(0, 1), (255, 10)],),
                                       ([(0, 1), (255, 10)],))
        """
        if isinstance(red, int) or isinstance(red, SoftInt):
            self.red = red
        elif isinstance(red, tuple):
            self.red = SoftInt(*red)
        if isinstance(green, int) or isinstance(green, SoftInt):
            self.green = green
        elif isinstance(green, tuple):
            self.green = SoftInt(*green)
        if isinstance(blue, int) or isinstance(blue, SoftInt):
            self.blue = blue
        elif isinstance(blue, tuple):
            self.blue = SoftInt(*blue)

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

    @classmethod
    def rgb_to_hex(cls, color):
        """
        Convert an ``(r, g, b)`` color tuple to a hexadecimal string.

        Alphabetical characters in the output will be capitalized.

        Args:
            color (tuple): An rgb color tuple of form: (int, int, int)

        Returns: string
        """
        return '#{0:02x}{1:02x}{2:02x}'.format(
            cls._bound_color_value(color[0]),
            cls._bound_color_value(color[1]),
            cls._bound_color_value(color[2])).upper()

    def get(self):
        """
        Get an rgb color tuple according to the probability distribution.

        Returns:
            tuple(int, int, int): A ``(red, green, blue)`` tuple.
        """
        if isinstance(self.red, SoftInt):
            red = self.red.get()
        else:
            red = self.red
        if isinstance(self.green, SoftInt):
            green = self.green.get()
        else:
            green = self.green
        if isinstance(self.blue, SoftInt):
            blue = self.blue.get()
        else:
            blue = self.blue

        return (red, green, blue)

    def get_as_hex(self):
        """
        Get a hexademical color according to the probability distribution.

        Equivalent to ``SoftColor.rgb_to_hex(self.get())``

        Returns:
            str: A hexademical color string
        """
        return SoftColor.rgb_to_hex(self.get())
