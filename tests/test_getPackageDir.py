#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
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
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import sys
import os
import unittest

import lsst.utils.tests
from lsst.utils import getPackageDir


class GetPackageDirTestCase(unittest.TestCase):
    def testBasics(self):
        utilsPath = getPackageDir("utils")
        self.assertTrue(os.path.isfile(os.path.join(utilsPath, "tests", "test_getPackageDir.py")))

        # Confirm that we have a correct Python exception and pex exception
        with self.assertRaises(LookupError) as cm:
            getPackageDir("nameOfNonexistendPackage2234q?#!")

        # Deliberately do not import pex_exceptions so as not to bias the
        # tests. Check for the name instead.
        self.assertIn("NotFoundError", type(cm.exception).__name__)

    def testUnicodeBasics(self):
        utilsPath = getPackageDir(u"utils")
        self.assertTrue(os.path.isfile(os.path.join(utilsPath, "tests", "test_getPackageDir.py")))


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    setup_module(sys.modules[__name__])
    unittest.main()
