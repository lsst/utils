#!/usr/bin/env python


import eups
import os
import pdb  # we may want to say pdb.set_trace()
import sys
import unittest

import lsst.utils.tests as utilsTests
import lsst.pex.exceptions as pexExcept
import lsst.utils.utilsLib as utilsLib
import lsst.utils as lsstutils

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class RaDecToStrTestCase(unittest.TestCase):
    """Convert angles to strings"""

    def setUp(self):
        self.goodData= [
            #Ra (deg)      Dec (deg)   Ra (rad)    Dec (rad)   Ra (str)       Dec (str)
            [0.00000000, 0.00000000, 0.00000000, 0.00000000, "00:00:00.00", "+00:00:00.00"],
            [0.00027778, 0.00000000, 0.00000485, 0.00000000, "00:00:00.07", "+00:00:00.00"],
            [0.00416667, 0.00000000, 0.00007272, 0.00000000, "00:00:01.00", "+00:00:00.00"],
            [0.01666667, 0.00000000, 0.00029089, 0.00000000, "00:00:04.00", "+00:00:00.00"],
            [1.00000000, 0.00000000, 0.01745329, 0.00000000, "00:04:00.00", "+00:00:00.00"],
            [15.00000000, 0.00000000, 0.26179939, 0.00000000, "01:00:00.00", "+00:00:00.00"],
            [0.00000000, 0.00027778, 0.00000000, 0.00000485, "00:00:00.00", "00:00:01.00"],
            [0.00000000, 0.00027778, 0.00000000, 0.00000485, "00:00:00.00", "+00:00:01.00"],
            [0.00000000, -0.00027778, 0.00000000, -0.00000485, "00:00:00.00", "-00:00:01.00"],
            [0.00000000, 0.01666667, 0.00000000, 0.00029089, "00:00:00.00", "00:01:00.00"],
            [0.00000000, 0.01666667, 0.00000000, 0.00029089, "00:00:00.00", "+00:01:00.00"],
            [0.00000000, -0.01666667, 0.00000000, -0.00029089, "00:00:00.00", "-00:01:00.00"],
            [0.00000000, 1.00000000, 0.00000000, 0.01745329, "00:00:00.00", "01:00:00.00"],
            [0.00000000, 1.00000000, 0.00000000, 0.01745329, "00:00:00.00", "+01:00:00.00"],
            [0.00000000, -1.00000000, 0.00000000, -0.01745329, "00:00:00.00", "-01:00:00.00"],
            [0.00000000, 15.00000000, 0.00000000, 0.26179939, "00:00:00.00", "15:00:00.00"],
            [0.00000000, 15.00000000, 0.00000000, 0.26179939, "00:00:00.00", "+15:00:00.00"],
            [0.00000000, -15.00000000, 0.00000000, -0.26179939, "00:00:00.00", "-15:00:00.00"],
        ]
        
        self.raDegCol=0
        self.decDegCol=1
        self.raRadCol=2
        self.decRadCol=3
        self.raStrCol=4
        self.decStrCol=5
        self.num = len(self.goodData)


    def tearDown(self):
        pass

    #
    # Testing numbers to strings
    #
    
    def testRaRadToStr(self):
        """"""
        
        for i in range(self.num):
            raRad = self.goodData[i][self.raRadCol]
            raStr = self.goodData[i][self.raStrCol]
            self.assertTrue(lsstutils.raRadToStr(raRad), raStr)
        

    def testRaDegToStr(self):
        """"""
        
        for i in range(self.num):
            raDeg = self.goodData[i][self.raDegCol]
            raStr = self.goodData[i][self.raStrCol]
            self.assertTrue(lsstutils.raDegToStr(raDeg), raStr)


    def testDecRadToStr(self):
        """"""
        
        for i in range(self.num):
            decRad = self.goodData[i][self.decRadCol]
            decStr = self.goodData[i][self.decStrCol]
            self.assertTrue(lsstutils.decRadToStr(decRad), decStr)
        

    def testDecDegToStr(self):
        """"""
        
        for i in range(self.num):
            decDeg = self.goodData[i][self.decDegCol]
            decStr = self.goodData[i][self.decStrCol]
            self.assertTrue(lsstutils.decDegToStr(decDeg), decStr)


    #
    # Testing strings to numbers
    #
    
    def testRaStrToRad(self):
        for i in range(self.num):
            raRad = self.goodData[i][self.raRadCol]
            raStr = self.goodData[i][self.raStrCol]
            self.assertAlmostEqual(lsstutils.raStrToRad(raStr)+1, raRad+1, 3)
        

    def testRaStrToDeg(self):
        for i in range(self.num):
            raDeg = self.goodData[i][self.raDegCol]
            raStr = self.goodData[i][self.raStrCol]
            self.assertAlmostEqual(lsstutils.raStrToDeg(raStr), raDeg, 3)

    #def testDecStrToRad(self):
        #for i in range(self.num):
            #decRad = self.goodData[i][self.decRadCol]
            #decStr = self.goodData[i][self.decStrCol]
            #self.assertTrue(lsstutils.decStrToRad(decStr), decRad)
        #
#
    def testDecStrToDeg(self):
        for i in range(self.num):
            decDeg = self.goodData[i][self.decDegCol]
            decStr = self.goodData[i][self.decStrCol]
            print "Test: %s == %.7f" %(decStr, decDeg)
            self.assertAlmostEqual(lsstutils.decStrToDeg(decStr), decDeg, 3)


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def suite():
    """Returns a suite containing all the test cases in this module."""

    utilsTests.init()

    suites = []
    suites += unittest.makeSuite(RaDecToStrTestCase)
    suites += unittest.makeSuite(utilsTests.MemoryTestCase)
    return unittest.TestSuite(suites)

def run(exit=False):
    """Run the tests"""
    utilsTests.run(suite(), exit)

if __name__ == "__main__":
    run(True)
