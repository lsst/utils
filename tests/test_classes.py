# This file is part of utils.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# Use of this source code is governed by a 3-clause BSD-style
# license that can be found in the LICENSE file.

import copy
import functools
import logging
import pickle
import unittest

from lsst.utils.classes import Singleton, cached_getter, immutable

log = logging.getLogger("test_classes")


class SingletonTestCase(unittest.TestCase):
    """Tests of the Singleton metaclass"""

    class IsSingleton(metaclass=Singleton):
        def __init__(self):
            self.data = {}
            self.id = 0

    class IsBadSingleton(IsSingleton):
        def __init__(self, arg):
            """A singleton can not accept any arguments."""
            self.arg = arg

    class IsSingletonSubclass(IsSingleton):
        def __init__(self):
            super().__init__()

    def testSingleton(self):
        one = SingletonTestCase.IsSingleton()
        two = SingletonTestCase.IsSingleton()

        # Now update the first one and check the second
        one.data["test"] = 52
        self.assertEqual(one.data, two.data)
        two.id += 1
        self.assertEqual(one.id, two.id)

        three = SingletonTestCase.IsSingletonSubclass()
        self.assertNotEqual(one.id, three.id)

        with self.assertRaises(TypeError):
            SingletonTestCase.IsBadSingleton(52)


class ImmutabilityTestCase(unittest.TestCase):
    @immutable
    class Immutable:
        def __init__(self, name: str, number: int):
            self.name = name
            self.number = number

        def __hash__(self) -> int:
            return hash((self.name, self.number))

    def testImmutable(self):
        im1 = ImmutabilityTestCase.Immutable("name", 42)
        im2 = ImmutabilityTestCase.Immutable("another", 0)
        self.assertEqual((im1.name, im1.number), ("name", 42))
        test_set = {im1, im2}
        self.assertIn(im2, test_set)

        with self.assertRaises(AttributeError):
            im1.name = "no"

        self.assertIs(copy.copy(im1), im1)

        # Pickling does not work without help and this tests that it
        # does not work.
        pickled = pickle.dumps(im1)
        im3 = pickle.loads(pickled)
        self.assertEqual(im3.__dict__, {})


class CacheTestCase(unittest.TestCase):
    class Cached1:
        """Cached getter using cached_getter. This can use slots."""

        __slots__ = ("value", "_cached_cache_value")

        def __init__(self, value: int):
            self.value = value

        @property
        @cached_getter
        def cache_value(self) -> int:
            log.info("Calculating cached value.")
            return self.value + 1

    class Cached2:
        """Cached getter using functools. This can not use slots."""

        def __init__(self, value: int):
            self.value = value

        @functools.cached_property
        def cache_value(self) -> int:
            log.info("Calculating cached value.")
            return self.value + 1

    def assertCache(self, cls):
        v1 = cls(42)
        self.assertEqual(v1.value, 42)

        with self.assertLogs(level=logging.INFO) as cm:
            cached_value = v1.cache_value
        self.assertEqual(cached_value, 43)
        self.assertEqual(cm.output, ["INFO:test_classes:Calculating cached value."])

        v1.value = 50
        self.assertEqual(v1.value, 50)
        with self.assertLogs(level=logging.INFO) as cm:
            cached_value = v1.cache_value
            log.info("Used cache.")
        self.assertEqual(cached_value, 43)
        self.assertEqual(cm.output, ["INFO:test_classes:Used cache."])

    def testCachedGetter(self):
        self.assertCache(CacheTestCase.Cached1)

    def testFunctoolsCachedProperty(self):
        self.assertCache(CacheTestCase.Cached2)


if __name__ == "__main__":
    unittest.main()
