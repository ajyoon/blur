import unittest

from .. import iching


class IChing(unittest.TestCase):
    def test_get_hexagram_three_coin(self):
        gram = iching.get_hexagram(method='THREE COIN')
        self.assertIsInstance(gram, tuple)
        self.assertEqual(len(gram), 2)
        self.assertTrue(1 <= gram[0] <= 64)
        self.assertTrue(1 <= gram[1] <= 64)

    def test_get_hexagram_yarrow(self):
        gram = iching.get_hexagram(method='YARROW')
        self.assertIsInstance(gram, tuple)
        self.assertEqual(len(gram), 2)
        self.assertTrue(1 <= gram[0] <= 64)
        self.assertTrue(1 <= gram[1] <= 64)

    def test_get_hexagram_naive(self):
        gram = iching.get_hexagram(method='NAIVE')
        self.assertIsInstance(gram, int)
        self.assertTrue(1 <= gram <= 64)

    def test_get_hexagram_with_invalid_method(self):
        with self.assertRaises(ValueError):
            gram = iching.get_hexagram(method='invalid method name')

    def test_long_description_dict_length(self):
        self.assertEqual(len(iching.descriptions), 64)
