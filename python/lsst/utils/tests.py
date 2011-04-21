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

"""Support code for running unit tests"""

import unittest
try:
    import lsst.daf.base as dafBase
except ImportError:
    dafBase = None
    
import lsst.pex.exceptions as pexExcept
import os
import sys
import gc

try:
    type(memId0)
except NameError:
    memId0 = 0                          # ignore leaked blocks with IDs before memId0
    nleakPrintMax = 20                  # maximum number of leaked blocks to print

def init():
    global memId0
    if dafBase:
        memId0 = dafBase.Citizen.getNextMemId() # used by MemoryTestCase

def run(suite, exit=True):
    """Exit with the status code resulting from running the provided test suite"""

    if unittest.TextTestRunner().run(suite).wasSuccessful():
        status = 0
    else:
        status = 1

    if exit:
        sys.exit(status)
    else:
        return status

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
        
class MemoryTestCase(unittest.TestCase):
    """Check for memory leaks since memId0 was allocated"""
    def setUp(self):
        pass

    def testLeaks(self):
        """Check for memory leaks in the preceding tests"""
        if dafBase:
            gc.collect()
            global memId0, nleakPrintMax
            nleak = dafBase.Citizen.census(0, memId0)
            if nleak != 0:
                print "\n%d Objects leaked:" % dafBase.Citizen.census(0, memId0)

                if nleak <= nleakPrintMax:
                    print dafBase.Citizen.census(dafBase.cout, memId0)
                else:
                    census = dafBase.Citizen.census()
                    print "..."
                    for i in range(nleakPrintMax - 1, -1, -1):
                        print census[i].repr()

                self.fail("Leaked %d blocks" % dafBase.Citizen.census(0, memId0))

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def findFileFromRoot(ifile):
    """Find file which is specified as a path relative to the toplevel directory;
    we start in $cwd and walk up until we find the file (or throw IOError if it doesn't exist)

    This is useful for running tests that may be run from <dir>/tests or <dir>"""
    
    if os.path.isfile(ifile):
        return ifile

    ofile = None
    file = ifile
    while file != "":
        dirname, basename = os.path.split(file)
        if ofile:
            ofile = os.path.join(basename, ofile)
        else:
            ofile = basename

        if os.path.isfile(ofile):
            return ofile

        file = dirname

    raise IOError, "Can't find %s" % ifile
