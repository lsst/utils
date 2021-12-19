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

import itertools
import sys
import unittest

import lsst.utils.tests

numCalls = 0  # Number of times testMethodDecorator gets called


@lsst.utils.tests.classParameters(word=["one", "two", "three", "four"], length=[3, 3, 5, 4])
class DecoratorTestCase(lsst.utils.tests.TestCase):
    """Test methodParameters and classParameters decorators"""

    def setUp(self):
        self.numCalls = 0
        self.methodDecorator = False  # testMethodDecorator fired

    def testClassDecorator(self):
        self.assertEqual(len(self.word), self.length)
        self.assertEqual(self.__class__.__name__, f"DecoratorTestCase_{self.word}_{self.length}")

    @lsst.utils.tests.methodParameters(
        xx=[1, 2, 3],
        yy=[9, 8, 7],
    )
    def testMethodDecorator(self, xx, yy):
        self.methodDecorator = True
        self.assertEqual(xx + yy, 10)
        self.numCalls += 1

    def tearDown(self):
        if self.methodDecorator:
            self.assertEqual(self.numCalls, 3)


@lsst.utils.tests.classParametersProduct(word=["one", "two"], number=[3, 4])
class DecoratorProductTestCase(lsst.utils.tests.TestCase):
    """Test methodParametersProduct and classParametersProduct decorators"""

    def setUp(self):
        self.combinations = set()
        self.methodDecorator = False  # testMethodDecorator fired

    def testClassDecorator(self):
        self.assertEqual(self.__class__.__name__, f"DecoratorProductTestCase_{self.word}_{self.number}")

    @lsst.utils.tests.methodParametersProduct(
        xx=[1, 2, 3],
        yy=[9, 8],
    )
    def testMethodDecorator(self, xx, yy):
        self.methodDecorator = True
        self.combinations.add((xx, yy))

    def tearDown(self):
        if self.methodDecorator:
            self.assertEqual(len(self.combinations), 6)
            for xx, yy in itertools.product((1, 2, 3), (9, 8)):
                self.assertIn((xx, yy), self.combinations)


def testDecorators():
    world = globals()
    assert "DecoratorTestCase_one_3" in world
    assert "DecoratorTestCase_two_3" in world
    assert "DecoratorTestCase_three_5" in world
    assert "DecoratorTestCase_four_4" in world

    assert "DecoratorProductTestCase_one_3" in world
    assert "DecoratorProductTestCase_one_4" in world
    assert "DecoratorProductTestCase_two_3" in world
    assert "DecoratorProductTestCase_two_4" in world


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    module = sys.modules[__name__]
    setup_module(module)
    testDecorators()
    unittest.main()
