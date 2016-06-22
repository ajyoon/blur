import unittest
import rand

class TestRand(unittest.TestCase):

    def test_weighted_option_rand(self):
        for i in range(1000):
            options = [(0, 1), (5, 2), (10, 5)]
            self.assertTrue(rand.weighted_option_rand(options) in [0, 5, 10])
