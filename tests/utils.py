#!/usr/bin/env python
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
import lsst.utils.utilsLib as utilsLib

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class UtilsTestCase(unittest.TestCase):
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

        utilsTests.assertRaisesLsstCpp(self, pexExcept.InvalidParameterException, tst)

    def testProductDirUnsetup(self):
        """Test the C++'s productDir returns the same value as the python one"""
        
        def tst():
            utilsLib.productDir("XXX utils XXX non existent")

        utilsTests.assertRaisesLsstCpp(self, pexExcept.NotFoundException, tst)

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
