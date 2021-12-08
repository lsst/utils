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
import sys
import unittest

import lsst.utils.tests
from lsst.utils import getPackageDir


@unittest.skipIf("UTILS_DIR" not in os.environ, "EUPS has not set up this package.")
class GetPackageDirTestCase(unittest.TestCase):
    def testBasics(self):
        utilsPath = getPackageDir("utils")
        self.assertTrue(os.path.isfile(os.path.join(utilsPath, "tests", "test_getPackageDir.py")))

        # Confirm that we have a correct Python exception and pex exception
        with self.assertRaises(LookupError):
            getPackageDir("nameOfNonexistendPackage2234q?#!")

    def testUnicodeBasics(self):
        utilsPath = getPackageDir("utils")
        self.assertTrue(os.path.isfile(os.path.join(utilsPath, "tests", "test_getPackageDir.py")))


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    setup_module(sys.modules[__name__])
    unittest.main()
