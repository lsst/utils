#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import sys
import unittest

import lsst.utils.tests


numCalls = 0  # Number of times testMethodDecorator gets called


@lsst.utils.tests.classParameters(
    word=["one", "two", "three", "four"],
    length=[3, 3, 5, 4]
)
class DecoratorTestCase(lsst.utils.tests.TestCase):
    def setUp(self):
        self.numCalls = 0

    def testClassDecorator(self):
        self.assertEqual(len(self.word), self.length)
        self.assertEqual(self.__class__.__name__, f"DecoratorTestCase_{self.word}_{self.length}")

    @lsst.utils.tests.methodParameters(
        xx=[1, 2, 3],
        yy=[9, 8, 7],
    )
    def testMethodDecorator(self, xx, yy):
        self.assertEqual(xx + yy, 10)
        self.numCalls += 1

    def teardown_method(self, method):
        if method.__name__ == "testMethodDecorator":
            self.assertEqual(self.numCalls, 3)


def testDecorators():
    world = globals()
    assert "DecoratorTestCase_one_3" in world
    assert "DecoratorTestCase_two_3" in world
    assert "DecoratorTestCase_three_5" in world
    assert "DecoratorTestCase_four_4" in world


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    module = sys.modules[__name__]
    setup_module(module)
    testDecorators()
    unittest.main()
