from __future__ import division

import unittest
import math
import random

from blur import soft


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
        test_object = soft.SoftOptions(options_input)
        # Test that options were correctly passed to the object
        # and that no side effects transformed the input list
        self.assertEqual(test_object.options,
                         options_original)

    def test_with_uniform_weights(self):
        options_original = ['Option 1', 'Option 2', 'Option 3']
        options_input = options_original[:]
        test_object = soft.SoftOptions.with_uniform_weights(options_input)
        # Test that no side effects transformed the input list
        self.assertEqual(options_input,
                         options_original)
        # Test that the weight of every object is the same
        self.assertTrue(all(w[1] == test_object.options[0][1]
                            for w in test_object.options))

    def test_with_random_weights(self):
        original_options = ['Option 1', 'Option 2', 'Option 3']
        test_object = soft.SoftOptions.with_random_weights(
            original_options)
        self.assertTrue(all(option[0] in original_options
                            for option in test_object.options))
        self.assertTrue(all(1 <= option[1] <= len(original_options)
                            for option in test_object.options))

    def test_get_returns_valid_options(self):
        options = [('Option 1', 5), ('Option 2', 3), ('Option 3', 1)]
        test_object = soft.SoftOptions(options)
        for i in range(10):
            self.assertIn(test_object.get(),
                          ['Option 1', 'Option 2', 'Option 3'])


class TestSoftBool(unittest.TestCase):
    def test__init__(self):
        test_object = soft.SoftBool(0.9)
        self.assertEqual(test_object.prob_true, 0.9)

    def test_get(self):
        test_object = soft.SoftBool(0.9)
        true_count = 0
        for i in range(100):
            if test_object.get():
                true_count += 1
        self.assertGreater(true_count, 60)


class TestSoftFloat(unittest.TestCase):
    def test_init__(self):
        original_weights = [(-5, 2), (3, 1), (5, 6)]
        weights = original_weights[:]
        test_object = soft.SoftFloat(weights)
        # Test that no side effects occured in passed list
        self.assertEqual(weights, original_weights)
        # Test that weights were passed correctly to the SoftFloat
        self.assertEqual(test_object.weights, weights)

    def test_bounded_uniform_without_weight_interval(self):
        lowest = -5
        highest = 5
        test_object = soft.SoftFloat.bounded_uniform(lowest, highest)
        # Test that only two weights were added
        self.assertEqual(len(test_object.weights), 2)
        # Test that the weight value in each weight is the same
        self.assertTrue(all(w[1] == test_object.weights[0][1]
                            for w in test_object.weights))

    def test_bounded_uniform_with_weight_interval(self):
        lowest = -5
        highest = 5
        weight_interval = 1
        test_object = soft.SoftFloat.bounded_uniform(
            lowest, highest, weight_interval)
        # Test that weights were added at specified interval
        self.assertEqual(len(test_object.weights), 11)
        # Test that the weight value in each weight is the same
        self.assertTrue(all(w[1] == test_object.weights[0][1]
                            for w in test_object.weights))

    def test_get(self):
        weights = [(-5, 2), (3, 1), (5, 6)]
        min_value = -5
        min_value = max_value = 5
        test_object = soft.SoftFloat(weights)
        for i in range(100):
            self.assertTrue(
                min_value <= test_object.get() <= max_value)


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
