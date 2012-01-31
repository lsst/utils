#!/usr/bin/env python

# 
# LSST Data Management System
# Copyright 2008, 2009, 2010 LSST Corporation.
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

import eups
import os
import pdb  # we may want to say pdb.set_trace()
import sys
import unittest

import lsst.utils.tests as utilsTests
import testLib

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

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
        self.assert_(result is None)

    def testReturnSelf(self):
        result = self.example.get2()
        self.assert_(result is self.example)
    
    def testReturnCopy(self):
        result = self.example.get3()
        self.assert_(result is not self.example)
        self.assert_(type(result) == testLib.Example)
        result.setValue("bar")
        self.assertEqual(self.example.getValue(), "foo")

    def testStringification(self):
        s = "Example(foo)"
        self.assertEqual(str(self.example), s)
        self.assertEqual(repr(self.example), s)

    def testEqualityComparison(self):
        self.assertNotEqual(self.example, testLib.Example("bar"))
        self.assertEqual(self.example, testLib.Example("foo"))
        self.assertNotEqual(self.example, [3,4,5]) # should not throw
        self.assertNotEqual([3,4,5], self.example) # should not throw

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def suite():
    """Returns a suite containing all the test cases in this module."""

    utilsTests.init()

    suites = []
    suites += unittest.makeSuite(SwigTestCase)
    suites += unittest.makeSuite(utilsTests.MemoryTestCase)
    return unittest.TestSuite(suites)

def run(exit=False):
    """Run the tests"""
    utilsTests.run(suite(), exit)

if __name__ == "__main__":
    run(True)
