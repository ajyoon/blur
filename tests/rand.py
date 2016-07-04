import unittest
from .. import rand


# Maybe break into one class per method? Or is that excessive?
class TestRand(unittest.TestCase):
    def test__linear_interp(self):
        # TODO: Build me
        pass

    def test__point_under_curve(self):
        # TODO: Build me
        pass

    def test_prob_bool(self):
        # Test guaranteed outcomes
        self.assertTrue(rand.prob_bool(100))
        self.assertTrue(rand.prob_bool(1))
        self.assertFalse(rand.prob_bool(0))
        self.assertFalse(rand.prob_bool(-100))

    def test_percent_possible(self):
        # TODO: Build me
        pass

    def test_pos_or_neg(self):
        # TODO: Build me
        pass

    def test_pos_or_neg_1(self):
        # TODO: Build me
        pass

    def test_merge_markov_weights_dicts(self):
        # TODO: Build me
        pass

    def test_weighted_option_rand(self):
        for i in range(1000):
            options = [(0, 1), (5, 2), (10, 5)]
            self.assertTrue(rand.weighted_option_rand(options) in [0, 5, 10])

    def test_interp_dict(self):
        # TODO: Build me
        pass

    def test_weighted_curve_rand(self):
        # TODO: Build me
        pass

    def test_weighted_sort(self):
        # TODO: Build me
        pass
