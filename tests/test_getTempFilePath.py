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
import time

import lsst.utils.tests


class GetTempFilePathTestCase(unittest.TestCase):
    def testBasics(self):
        with lsst.utils.tests.getTempFilePath(".txt") as tmpFile:
            # Path will have unique component so do not test full equality
            self.assertIn("test_getTempFilePath_testBasics", tmpFile)
            self.assertTrue(tmpFile.endswith(".txt"))
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
            # Path will have unique component so do not test full equality
            self.assertIn("test_getTempFilePath_%s" % (funcName,), tmpFile)
            self.assertTrue(tmpFile.endswith(".fits"))
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


class TestNameClash1(unittest.TestCase):
    """The TestNameClashN classes are used to check that getTempFilePath
    does not use the same name across different test classes in the same
    file even if they have the same test methods."""

    def testClash(self):
        """Create the temp file and pause before trying to delete it."""
        with lsst.utils.tests.getTempFilePath(".fits") as tmpFile:
            with open(tmpFile, "w") as f:
                f.write("foo\n")
            time.sleep(0.2)
            self.assertTrue(os.path.exists(tmpFile))


class TestNameClash2(unittest.TestCase):

    def testClash(self):
        """Pause a little before trying to create the temp file. The pause
        time is less than the time that TestNameClash1 is pausing."""
        with lsst.utils.tests.getTempFilePath(".fits") as tmpFile:
            time.sleep(0.1)
            with open(tmpFile, "w") as f:
                f.write("foo\n")
            self.assertTrue(os.path.exists(tmpFile))


class TestNameClash3(unittest.TestCase):

    def testClash(self):
        """Create temp file and remove it without pauses."""
        with lsst.utils.tests.getTempFilePath(".fits") as tmpFile:
            with open(tmpFile, "w") as f:
                f.write("foo\n")
            self.assertTrue(os.path.exists(tmpFile))


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    setup_module(sys.modules[__name__])
    unittest.main()
