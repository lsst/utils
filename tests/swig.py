#!/usr/bin/env python

#
# LSST Data Management System
# Copyright 2008-2015 LSST/AURA
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
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
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <http://www.lsstcorp.org/LegalNotices/>.
#

"""
Tests for SWIG utilities

Run with:
   python swig.py
or
   python
   >>> import swig; swig.run()
"""
from builtins import str
from past.builtins import long

import unittest
import numpy

import lsst.utils.tests
import testLib


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


class SwigTestCase(unittest.TestCase):
    """A test case for SWIG utilities in p_lsstSwig.i"""

    def setUp(self):
        self.example = testLib.Example("foo")

    def testConstructors(self):
        self.assertEqual(self.example.getValue(), "foo")
        self.assertRaises(Exception, testLib.Example, [5])
        self.assertEqual(testLib.Example("bar").getValue(), "bar")

    def testReturnNone(self):
        result = self.example.get1()
        self.assertIsNone(result)

    def testReturnSelf(self):
        result = self.example.get2()
        self.assertIs(result, self.example)

    def testReturnCopy(self):
        result = self.example.get3()
        self.assertIsNot(result, self.example)
        self.assertTrue(type(result) == testLib.Example)
        result.setValue("bar")
        self.assertEqual(self.example.getValue(), "foo")

    def testStringification(self):
        s = "Example(foo)"
        self.assertEqual(str(self.example), s)
        self.assertEqual(repr(self.example), s)

    def testEqualityComparison(self):
        self.assertNotEqual(self.example, testLib.Example("bar"))
        self.assertEqual(self.example, testLib.Example("foo"))
        self.assertNotEqual(self.example, [3, 4, 5])  # should not throw
        self.assertNotEqual([3, 4, 5], self.example)  # should not throw

    def assertAccepts(self, function, value, msg):
        try:
            self.assertEqual(function(value), value, msg="%s: %r != %r" % (msg, function(value), value))
        except TypeError:
            self.fail(msg)

    def checkNumericTypemap(self, function):
        self.assertAccepts(function, int(1), msg="Failure passing int to %s" % function.__name__)
        self.assertAccepts(function, long(1), msg="Failure passing long to %s" % function.__name__)
        self.assertRaises((TypeError, NotImplementedError),
                          function, "5")  # should fail to convert even numeric strings
        # We should be able to coerce integers with different signedness and size to any numeric
        # type argument (as long as we don't trigger overflow)
        for size in (8, 16, 32, 64):
            for name in ("int%d" % size, "uint%d" % size):
                array = numpy.ones(1, dtype=getattr(numpy, name))
                self.assertAccepts(function, array[0],
                                   msg="Failure passing numpy.%s to %s" % (name, function.__name__))

    def checkFloatingTypemap(self, function):
        self.checkNumericTypemap(function)
        self.assertAccepts(function, float(3.5), "Failure passing float to %s" % function.__name__)

    def checkIntegerTypemap(self, function, size):
        # if we pass an integer that doesn't fit in the C++ argument type, we should raise
        # OverflowError
        self.checkNumericTypemap(function)
        tooBig = 2**(size + 1)
        self.assertRaises(OverflowError, function, tooBig)

    def testNumericTypemaps(self):
        """Test our customized numeric scalar typemaps, including support for NumPy scalars.
        """
        self.checkFloatingTypemap(testLib.accept_float32)
        self.checkFloatingTypemap(testLib.accept_cref_float32)
        self.checkFloatingTypemap(testLib.accept_cref_float64)
        for size in (8, 16, 32, 64):
            self.checkIntegerTypemap(getattr(testLib, "accept_int%d" % size), size)
            self.checkIntegerTypemap(getattr(testLib, "accept_uint%d" % size), size)
            self.checkIntegerTypemap(getattr(testLib, "accept_cref_int%d" % size), size)
            self.checkIntegerTypemap(getattr(testLib, "accept_cref_uint%d" % size), size)
        # Test that we choose the floating point overload when we pass a float,
        # and we get the integer overload when we pass an int.
        # We can't ever distinguish between different kinds of ints or different
        # kinds of floats in an overloading context, but that's a Swig limitation.
        self.assertEqual(testLib.getName(int(1)), "int")
        self.assertEqual(testLib.getName(float(1)), "double")


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


def setup_module(module):
    lsst.utils.tests.init()

if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
