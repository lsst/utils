# This file is part of utils.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# Use of this source code is governed by a 3-clause BSD-style
# license that can be found in the LICENSE file.

import os.path
import sys
import time
import unittest

import lsst.utils.tests

"""
This file contains tests for lsst.utils.tests.getTempFilePath.

The TestNameClashN classes are used to check that getTempFilePath
does not use the same name across different test classes in the same
file even if they have the same test methods. They are distinct classes
with the same test method in an attempt to trigger a race condition
whereby context managers use the same name and race to delete the file.
The sleeps are there to ensure the race condition occurs in older versions
of this package. This should not happen as of DM-13046."""


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


class TestNested(unittest.TestCase):
    """Tests of the use of getTempFilePath in nested context managers."""

    def testNested(self):
        with lsst.utils.tests.getTempFilePath(".fits") as tmpFile1:
            with lsst.utils.tests.getTempFilePath(".fits") as tmpFile2:
                self.assertNotEqual(tmpFile1, tmpFile2)
                with open(tmpFile1, "w") as f1:
                    f1.write("foo\n")
                with open(tmpFile2, "w") as f2:
                    f2.write("foo\n")
            self.assertTrue(os.path.exists(tmpFile1))
            self.assertFalse(os.path.exists(tmpFile2))
        self.assertFalse(os.path.exists(tmpFile1))


class TestExpected(unittest.TestCase):
    """Tests that we get files when we expect to get them and we get upset
    when we don't get them."""

    def testOutputExpected(self):
        with lsst.utils.tests.getTempFilePath(".txt") as tmpFile:
            with open(tmpFile, "w") as f:
                f.write("foo\n")
        self.assertFalse(os.path.exists(tmpFile))

        with self.assertRaises(RuntimeError):
            with lsst.utils.tests.getTempFilePath(".txt", expectOutput=True) as tmpFile:
                pass

        with self.assertRaises(RuntimeError):
            with lsst.utils.tests.getTempFilePath(".txt") as tmpFile:
                pass

    def testOutputUnexpected(self):
        with self.assertRaises(RuntimeError):
            with lsst.utils.tests.getTempFilePath(".txt", expectOutput=False) as tmpFile:
                with open(tmpFile, "w") as f:
                    f.write("foo\n")

        with lsst.utils.tests.getTempFilePath(".txt", expectOutput=False) as tmpFile:
            pass
        self.assertFalse(os.path.exists(tmpFile))


class TestNameClash1(unittest.TestCase):
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
