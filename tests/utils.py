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
Tests for utilities

Run with:
   python utils.py
or
   python
   >>> import utils; utils.run()
"""

import eups
import pdb  # we may want to say pdb.set_trace()
import unittest
import numpy

import lsst.utils.tests as utilsTests
import lsst.pex.exceptions as pexExcept
import lsst.utils.utilsLib as utilsLib

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class UtilsTestCase(utilsTests.TestCase):
    """A test case for Utils"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testProductDir(self):
        """Test the C++'s productDir returns the same value as the python one"""
        
        self.assertTrue(utilsLib.productDir("utils") == eups.productDir("utils"))

    def testProductDirCurrent(self):
        """Test the C++'s productDir returns the same value as the python one"""
        
        def tst():
            utilsLib.productDir("utils", "current")

        self.assertRaises(pexExcept.InvalidParameterError, tst)

    def testProductDirUnsetup(self):
        """Test the C++'s productDir returns the same value as the python one"""
        
        def tst():
            utilsLib.productDir("XXX utils XXX non existent")

        self.assertRaises(pexExcept.NotFoundError, tst)

    def testCompareArrays(self):
        self.assertClose(0.0, 0.0)
        self.assertClose(0.0, 1E-8, atol=1E-7)
        self.assertClose(0.0, 1E-8, atol=1E-7, rtol=None)
        self.assertClose(0.0, 1E-8, atol=None, rtol=1E-5, relTo=1E-2)
        self.assertNotClose(0.0, 1E-8, atol=1E-9)
        self.assertNotClose(0.0, 1E-8, atol=1E-9, rtol=None)
        self.assertNotClose(0.0, 1E-8, atol=None, rtol=1E-7, relTo=1E-2)
        self.assertClose(100, 100 + 1E-8, rtol=1E-7)
        self.assertClose(100, 100 + 1E-8, rtol=1E-7, atol=None)
        self.assertClose(100, 100 + 1E-8, rtol=1E-7, relTo=100.0)
        self.assertNotClose(100, 100 + 1E-8, rtol=1E-12)
        self.assertNotClose(100, 100 + 1E-8, rtol=1E-12, atol=None)
        self.assertNotClose(100, 100 + 1E-8, rtol=1E-12, relTo=100.0)
        a = numpy.zeros((5, 5), dtype=float)
        b = numpy.zeros((5, 5), dtype=float)
        self.assertClose(a, b)
        self.assertClose(a, b, rtol=None)
        self.assertClose(a, b, atol=None)
        self.assertRaises(ValueError, self.assertClose, a, b, atol=None, rtol=None)
        b[:,:] = 1E-8
        self.assertClose(a, b, atol=1E-7)
        self.assertClose(a, 1E-8, atol=1E-7)
        self.assertClose(a, b, atol=1E-7, rtol=None)
        self.assertNotClose(a, b, atol=1E-9)
        self.assertNotClose(a, b, atol=1E-9, rtol=None)
        a[:,:] = 100.0
        b[:,:] = 100.0 + 1E-8
        self.assertClose(a, b, rtol=1E-7)
        self.assertClose(a, 100.0 + 1E-8, rtol=1E-7)
        self.assertClose(a, b, rtol=1E-7, atol=None)
        self.assertClose(a, b, rtol=1E-7, relTo=100.0)
        self.assertNotClose(a, b, rtol=1E-12)
        self.assertNotClose(a, b, rtol=1E-12, atol=None)
        self.assertNotClose(a, b, rtol=1E-12, relTo=100.0)
        a[:,:] = numpy.arange(-12,13).reshape(5,5)
        b[:,:] = a
        b[2,:] += numpy.linspace(-1E-4, 1E-4, 5)
        self.assertClose(a, b, rtol=1E-3, atol=1E-4)
        if False:
            # set to True to test plotting and printing by-eye when tests fail
            # should see failures on the center row of the 5x5 image, but not the very center point
            self.assertClose(a, b, rtol=1E-6, plotOnFailure=True)
        

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def suite():
    """Returns a suite containing all the test cases in this module."""

    utilsTests.init()

    suites = []
    suites += unittest.makeSuite(UtilsTestCase)
    suites += unittest.makeSuite(utilsTests.MemoryTestCase)
    return unittest.TestSuite(suites)

def run(exit=False):
    """Run the tests"""
    utilsTests.run(suite(), exit)

if __name__ == "__main__":
    run(True)
