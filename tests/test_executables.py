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

import os
import unittest

import lsst.utils.tests


class ExplicitBinaryTester(lsst.utils.tests.ExecutablesTestCase):
    def testSimpleExe(self):
        """Test explicit shell script"""
        self.assertExecutable(
            "testexe.sh", root_dir=os.path.dirname(__file__), args=["-h"], msg="testexe.sh failed"
        )

        # Try a non-existent test
        with self.assertRaises(unittest.SkipTest):
            self.assertExecutable("testexe-missing.sh")

        # Force test to fail, explicit fail message
        with self.assertRaises(AssertionError):
            self.assertExecutable(
                "testexe.sh", root_dir=os.path.dirname(__file__), args=["-f"], msg="testexe.sh failed"
            )

        # Force script to fail, default fail message
        with self.assertRaises(AssertionError):
            self.assertExecutable("testexe.sh", root_dir=os.path.dirname(__file__), args=["-f"])


class UtilsBinaryTester(lsst.utils.tests.ExecutablesTestCase):
    pass


EXECUTABLES = None
UtilsBinaryTester.create_executable_tests(__file__, EXECUTABLES)

if __name__ == "__main__":
    unittest.main()
