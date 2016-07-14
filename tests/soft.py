from __future__ import division

import unittest
import math
import random

from .. import soft


class TestSoftObject(unittest.TestCase):
    def test_init_is_not_implemented(self):
        """Test that SoftObject.__init__() is not implemented."""
        with self.assertRaises(NotImplementedError):
            soft_object = soft.SoftObject()

    def test_has_get_method(self):
        """Test that SoftObject.get() exists."""
        self.assertTrue(hasattr(soft.SoftObject, 'get'))


class TestSoftOptions(unittest.TestCase):
    def test_init__(self):
        options_original = [('Option 1', 5), ('Option 2', 3), ('Option 3', 1)]
        options_input = options_original[:]
        softoptions = soft.SoftOptions(options_input)
        # Test that options were correctly passed to the object
        # and that no side effects transformed the input list
        self.assertEqual(softoptions.options,
                         options_original)

    def test_with_uniform_weights(self):
        options_original = ['Option 1', 'Option 2', 'Option 3']
        options_input = options_original[:]
        softoptions = soft.SoftOptions.with_uniform_weights(options_input)
        # Test that no side effects transformed the input list
        self.assertEqual(options_input,
                         options_original)
        # Test that the weight of every object is the same
        self.assertTrue(all(w[1] == softoptions.options[0][1]
                            for w in softoptions.options))


    def test_with_random_weights(self):
        # TODO: Build me!
        pass

    def test_get(self):
        # TODO: Build me!
        pass


class TestSoftBool(unittest.TestCase):
    def test___init__(self):
        # TODO: Build me!
        pass

    def test_get(self):
        # TODO: Build me!
        pass


class TestSoftFloat(unittest.TestCase):
    def test_init__(self):
        # TODO: Build me!
        pass

    def test_bounded_uniform(self):
        # TODO: Build me!
        pass

    def test_get(self):
        # TODO: Build me!
        pass


class TestSoftInt(unittest.TestCase):
    def test_init__(self):
        # TODO: Build me!
        pass

    def test_bounded_uniform(self):
        # TODO: Build me!
        pass

    def test_get(self):
        # TODO: Build me!
        pass


class TestSoftColor(unittest.TestCase):
    def test_init__(self):
        # TODO: Build me!
        pass

    def test_bound_color_value(self):
        # TODO: Build me!
        pass

    def test_to_hex(self):
        # TODO: Build me!
        pass

    def test_get(self):
        # TODO: Build me!
        pass
