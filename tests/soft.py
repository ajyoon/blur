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
        max_value = 5
        test_object = soft.SoftFloat(weights)
        for i in range(50):
            self.assertTrue(
                min_value <= test_object.get() <= max_value)


class TestSoftInt(unittest.TestCase):
    def test_init__(self):
        original_weights = [(-5, 2), (3, 1), (5, 6)]
        weights = original_weights[:]
        test_object = soft.SoftInt(weights)
        # Test that no side effects occured in passed list
        self.assertEqual(weights, original_weights)
        # Test that weights were passed correctly to the SoftFloat
        self.assertEqual(test_object.weights, weights)

    def test_bounded_uniform_without_weight_interval(self):
        lowest = -5
        highest = 5
        test_object = soft.SoftInt.bounded_uniform(lowest, highest)
        # Test that only two weights were added
        self.assertEqual(len(test_object.weights), 2)
        # Test that the weight value in each weight is the same
        self.assertTrue(all(w[1] == test_object.weights[0][1]
                            for w in test_object.weights))

    def test_bounded_uniform_with_weight_interval(self):
        lowest = -5
        highest = 5
        weight_interval = 1
        test_object = soft.SoftInt.bounded_uniform(
            lowest, highest, weight_interval)
        # Test that weights were added at specified interval
        self.assertEqual(len(test_object.weights), 11)
        # Test that the weight value in each weight is the same
        self.assertTrue(all(w[1] == test_object.weights[0][1]
                            for w in test_object.weights))

    def test_get(self):
        weights = [(-5, 2), (3, 1), (5, 6)]
        min_value = -5
        max_value = 5
        test_object = soft.SoftInt(weights)
        for i in range(50):
            got_value = test_object.get()
            self.assertTrue(min_value <= got_value <= max_value)
            self.assertIsInstance(got_value, int)


class TestSoftColor(unittest.TestCase):
    def test_init_from_int_values(self):
        red = 50
        green = 80
        blue = 90
        test_object = soft.SoftColor(red, green, blue)
        # Test that types were not converted
        self.assertIsInstance(test_object.red, int)
        self.assertIsInstance(test_object.green, int)
        self.assertIsInstance(test_object.blue, int)
        # Test that attributes were assigned correctly
        self.assertEqual(test_object.red, red)
        self.assertEqual(test_object.green, green)
        self.assertEqual(test_object.blue, blue)

    def test_init_from_existing_softints(self):
        red = soft.SoftInt.bounded_uniform(0, 255)
        green = soft.SoftInt.bounded_uniform(0, 255)
        blue = soft.SoftInt.bounded_uniform(0, 255)
        test_object = soft.SoftColor(red, green, blue)
        # Test that attributes were assigned correctly
        self.assertEqual(test_object.red, red)
        self.assertEqual(test_object.green, green)
        self.assertEqual(test_object.blue, blue)

    def test_init_from_tuples_of_args_for_softints(self):
        red_args = ([(0, 1), (255, 10)],)
        green_args = ([(0, 1), (255, 10)],)
        blue_args = ([(0, 1), (255, 10)],)
        test_object = soft.SoftColor(red_args, green_args, blue_args)
        # Test that SoftInt's were initialized correctly from args
        self.assertIsInstance(test_object.red, soft.SoftInt)
        self.assertIsInstance(test_object.green, soft.SoftInt)
        self.assertIsInstance(test_object.blue, soft.SoftInt)
        # Test that attributes were assigned correctly
        self.assertEqual(test_object.red.weights, [(0, 1), (255, 10)])
        self.assertEqual(test_object.green.weights, [(0, 1), (255, 10)])
        self.assertEqual(test_object.blue.weights, [(0, 1), (255, 10)])

    def test_init_with_invalid_arg_types_raises_TypeError(self):
        with self.assertRaises(TypeError):
            # Test red
            test_object = soft.SoftColor('NONSENSE', 255, 255)
        with self.assertRaises(TypeError):
            # Test green
            test_object = soft.SoftColor(255, 'NONSENSE', 255)
        with self.assertRaises(TypeError):
            # Test blue
            test_object = soft.SoftColor(255, 255, 'NONSENSE')

    def test_bound_color_value(self):
        # Test that values below 0 return 0
        self.assertEqual(soft.SoftColor._bound_color_value(-1), 0)
        # Test that values between 0 and 255 return unchanged
        self.assertEqual(soft.SoftColor._bound_color_value(50), 50)
        # Test that values above 255 return 255
        self.assertEqual(soft.SoftColor._bound_color_value(256), 255)

    def test_rgb_to_hex(self):
        self.assertEqual(soft.SoftColor.rgb_to_hex((128, 128, 128)),
                         '#808080')

    def test_get_with_only_int_color_types(self):
        red_input = 128
        green_input = 200
        blue_input = 255
        test_object = soft.SoftColor(red_input, green_input, blue_input)
        red, green, blue = test_object.get()
        # Test that only int's were returned
        self.assertIsInstance(red, int)
        self.assertIsInstance(green, int)
        self.assertIsInstance(blue, int)
        # Test that return values are within expected ranges
        self.assertEqual(red, red_input)
        self.assertEqual(green, green_input)
        self.assertEqual(blue, blue_input)

    def test_get_with_only_softint_color_types(self):
        red_input = soft.SoftInt.bounded_uniform(1, 2)
        green_input = soft.SoftInt.bounded_uniform(3, 4)
        blue_input = soft.SoftInt.bounded_uniform(5, 6)
        test_object = soft.SoftColor(red_input, green_input, blue_input)
        red, green, blue = test_object.get()
        # Test that only int's were returned
        self.assertIsInstance(red, int)
        self.assertIsInstance(green, int)
        self.assertIsInstance(blue, int)
        # Test that return values are within expected ranges
        self.assertTrue(1 <= red <= 2)
        self.assertTrue(3 <= green <= 4)
        self.assertTrue(5 <= blue <= 6)

    def test_get_with_mixed_color_types(self):
        red_input = soft.SoftInt.bounded_uniform(0, 2)
        green_input = ([(200, 1), (255, 10)],)
        blue_input = 255
        test_object = soft.SoftColor(red_input, green_input, blue_input)
        red, green, blue = test_object.get()
        # Test that only int's were returned
        self.assertIsInstance(red, int)
        self.assertIsInstance(green, int)
        self.assertIsInstance(blue, int)
        # Test that return values are within expected ranges
        self.assertTrue(0 <= red <= 2)
        self.assertTrue(200 <= green <= 255)
        self.assertEqual(blue, 255)

    def test_get_as_hex(self):
        test_object = soft.SoftColor(128, 200, 255)
        hex_color = test_object.get_as_hex()
        # Convert to uppercase to separate upper/lower case
        #   into a different test
        self.assertEqual(hex_color.upper(), '#80C8FF')

    def test_get_as_hex_returns_uppercase(self):
        test_object = soft.SoftColor(128, 200, 255)
        hex_color = test_object.get_as_hex()
        self.assertEqual(hex_color, '#80C8FF')
