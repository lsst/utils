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
import os
import pdb  # we may want to say pdb.set_trace()
import sys
import unittest

import lsst.utils.tests as utilsTests
import lsst.pex.exceptions as pexExcept
import lsst.utils

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class UtilsTestCase(unittest.TestCase):
    """A test case for Utils"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testProductDir(self):
        """Test the C++'s productDir returns the same value as the python one"""
        
        self.assertTrue(lsst.utils.productDir("utils") == eups.productDir("utils"))

    def testProductDirCurrent(self):
        """Test the C++'s productDir returns the same value as the python one"""
        
        def tst():
            lsst.utils.productDir("utils", "current")

        self.assertRaises(pexExcept.InvalidParameterException, tst)

    def testProductDirUnsetup(self):
        """Test the C++'s productDir returns the same value as the python one"""
        
        def tst():
            lsst.utils.productDir("XXX utils XXX non existent")

        self.assertRaises(pexExcept.NotFoundException, tst)

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
