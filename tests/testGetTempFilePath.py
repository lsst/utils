#
# LSST Data Management System
# Copyright 2016 LSST Corporation.
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
import sys
import unittest
import os.path

import lsst.utils.tests


class GetTempFilePathTestCase(unittest.TestCase):
    def testBasics(self):
        with lsst.utils.tests.getTempFilePath(".txt") as tmpFile:
            baseName = os.path.basename(tmpFile)
            self.assertEqual(baseName, "testGetTempFilePath_testBasics.txt")
            f = open(tmpFile, "w")
            f.write("foo\n")
            f.close()
        self.assertFalse(os.path.exists(tmpFile))

    def testMultipleCallDepth(self):
        """Test getTempFile with multiple call depth"""
        funcName = "testMultipleCallDepth"
        self.runGetTempFile(funcName)
        self.runLevel2(funcName)
        self.runLevel3(funcName)

    def runGetTempFile(self, funcName):
        with lsst.utils.tests.getTempFilePath(".fits") as tmpFile:
            baseName = os.path.basename(tmpFile)
            self.assertEqual(baseName,
                             "testGetTempFilePath_%s.fits" % (funcName,))
            f = open(tmpFile, "w")
            f.write("foo\n")
            f.close()
        self.assertFalse(os.path.exists(tmpFile))

    def runLevel2(self, funcName):
        """Call runGetTempFile"""
        self.runGetTempFile(funcName)

    def runLevel3(self, funcName):
        """Call runLevel2, which calls runGetTempFile"""
        self.runLevel2(funcName)


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    setup_module(sys.modules[__name__])
    unittest.main()
