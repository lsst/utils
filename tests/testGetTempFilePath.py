#!/usr/bin/env python2
import unittest
import os.path

import lsst.utils.tests


def setup_module(module):
    lsst.utils.tests.init()


class GetTempFilePathTestCase(unittest.TestCase):
    """Test case for getTempFilePath"""

    def testBasics(self):
        with lsst.utils.tests.getTempFilePath(".txt") as tmpFile:
            baseName = os.path.basename(tmpFile)
            self.assertEqual(baseName, "testGetTempFilePath_testBasics.txt")
            f = file(tmpFile, "w")
            f.write("foo\n")
            f.close()
        self.assertFalse(os.path.exists(tmpFile))

    def testMultipleCallDepth(self):
        """Test getTempFile with multiple call depth
        """
        funcName = "testMultipleCallDepth"
        self.runGetTempFile(funcName)
        self.runLevel2(funcName)
        self.runLevel3(funcName)

    def runGetTempFile(self, funcName):
        with lsst.utils.tests.getTempFilePath(".fits") as tmpFile:
            baseName = os.path.basename(tmpFile)
            self.assertEqual(baseName, "testGetTempFilePath_%s.fits" % (funcName,))
            f = open(tmpFile, "w")
            f.write("foo\n")
            f.close()
        self.assertFalse(os.path.exists(tmpFile))

    def runLevel2(self, funcName):
        """Call runGetTempFile
        """
        self.runGetTempFile(funcName)

    def runLevel3(self, funcName):
        """Call runLevel2, which calls runGetTempFile
        """
        self.runLevel2(funcName)


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
