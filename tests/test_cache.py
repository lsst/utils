from __future__ import absolute_import, division, print_function

from builtins import int

import unittest

import lsst.utils.tests
from lsst.pex.exceptions import NotFoundError
from _cache import NumbersCache


def numberToWords(value):
    """Convert a number in the range [0, 1000) to words"""
    assert value >= 0 and isinstance(value, int), "Only non-negative integers"
    if value < 20:
        return {
            0: "zero",
            1: "one",
            2: "two",
            3: "three",
            4: "four",
            5: "five",
            6: "six",
            7: "seven",
            8: "eight",
            9: "nine",
            10: "ten",
            11: "eleven",
            12: "twelve",
            13: "thirteen",
            14: "fourteen",
            15: "fifteen",
            16: "sixteen",
            17: "seventeen",
            18: "eighteen",
            19: "nineteen",
        }[value]
    if value < 100:
        tens = value//10
        ones = value % 10
        return {
            2: "twenty",
            3: "thirty",
            4: "forty",
            5: "fifty",
            6: "sixty",
            7: "seventy",
            8: "eighty",
            9: "ninety",
        }[tens] + (("-" + numberToWords(ones)) if ones > 0 else "")
    assert value < 1000, "Value exceeds limit of 999"
    hundreds = value//100
    rest = value % 100
    return numberToWords(hundreds) + " hundred" + ((" " + numberToWords(rest)) if rest > 0 else "")


class CacheTestCase(lsst.utils.tests.TestCase):
    """Tests of lsst.utils.Cache"""
    def check(self, addFunction):
        """Exercise the Cache

        The `addFunction` should take a cache and number,
        and add the number (and its corresponding string)
        into the cache.
        """
        capacity = 10
        cache = NumbersCache(capacity)
        self.assertEqual(cache.size(), 0, "Starts empty")
        self.assertEqual(cache.capacity(), capacity, "Capacity as requested")
        maximum = 20
        for ii in range(maximum):
            addFunction(cache, ii)
        self.assertEqual(cache.size(), capacity, "Filled to capacity")
        self.assertEqual(cache.capacity(), capacity, "Capacity unchanged")
        for ii in range(maximum - capacity):
            self.assertNotIn(ii, cache, "Should have been expunged")
        expectedContents = list(range(maximum - 1, maximum - capacity - 1, -1))  # Last in, first out
        actualContents = cache.keys()
        for ii in expectedContents:
            self.assertIn(ii, cache, "Should be present")
            self.assertEqual(cache[ii], numberToWords(ii), "Value accessible and as expected")
        self.assertListEqual(actualContents, expectedContents, "Contents are as expected")
        with self.assertRaises(NotFoundError):
            cache[maximum - capacity - 1]
        newCapacity = 5
        cache.reserve(newCapacity)
        # The new list of contents is smaller, but also reversed because we've gone through the cache
        # touching items.
        newExpectedContents = list(reversed(expectedContents))[:newCapacity]
        self.assertEqual(cache.capacity(), newCapacity, "Capacity changed")
        self.assertEqual(cache.size(), newCapacity, "Size changed to correspond to new capacity")
        self.assertListEqual(cache.keys(), newExpectedContents, "Most recent kept")
        cache.flush()
        self.assertEqual(cache.size(), 0, "Flushed everything out")
        self.assertEqual(cache.capacity(), newCapacity, "Capacity unchanged")
        return cache

    def testDirect(self):
        """Directly add key,value pairs into the cache with Cache.add"""
        self.check(lambda cache, index: cache.add(index, numberToWords(index)))

    def testLazy(self):
        """Exercise the lazy function call in Cache.operator()"""
        def addFunction(cache, index):
            value = cache(index, lambda ii: numberToWords(ii))
            self.assertEqual(value, numberToWords(index))

        cache = self.check(addFunction)

        # Check that the function call doesn't fire when we pull out something that's in there already
        def trap(key):
            raise AssertionError("Failed")

        for index in cache.keys():
            value = cache(index, trap)
            self.assertEqual(value, numberToWords(index))

        # Check that this checking technique actually works...
        with self.assertRaises(AssertionError):
            cache(999, trap)


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    import sys
    setup_module(sys.modules[__name__])
    unittest.main()
