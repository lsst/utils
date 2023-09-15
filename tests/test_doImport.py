# This file is part of utils.
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

import inspect
import unittest

import lsst.utils.tests
from lsst.utils import doImport, doImportType


class ImportTestCase(lsst.utils.tests.TestCase):
    """Basic tests of doImport."""

    def testDoImport(self):
        c = doImport("lsst.utils.tests.TestCase")
        self.assertEqual(c, lsst.utils.tests.TestCase)

        c = doImport("lsst.utils.tests.TestCase.assertFloatsAlmostEqual")
        self.assertEqual(c, lsst.utils.tests.TestCase.assertFloatsAlmostEqual)

        c = doImport("lsst.utils.doImport")
        self.assertEqual(type(c), type(doImport))
        self.assertTrue(inspect.isfunction(c))

        c = doImport("lsst.utils")
        self.assertTrue(inspect.ismodule(c))

        with self.assertRaises(ImportError):
            doImport("lsst.utils.tests.TestCase.xyprint")

        with self.assertRaises(ImportError):
            doImport("lsst.utils.nothere")

        with self.assertRaises(ModuleNotFoundError):
            doImport("missing module")

        with self.assertRaises(ModuleNotFoundError):
            doImport("lsstdummy.import.fail")

        with self.assertRaises(ImportError):
            doImport("lsst.import.fail")

        with self.assertRaises(ImportError):
            doImport("lsst.utils.x")

        with self.assertRaises(TypeError):
            doImport([])

        # Use a special test module
        with self.assertRaises(RuntimeError):
            doImport("import_test.two.three.runtime")

        with self.assertRaises(ImportError):
            doImport("import_test.two.three.success.not_okay")

        with self.assertRaises(ImportError):
            doImport("import_test.two.three.fail")

        # Check that the error message reports the notthere failure
        try:
            doImport("import_test.two.three.fail.myfunc")
        except ImportError as e:
            self.assertIn("notthere", str(e))

        c = doImport("import_test.two.three.success")
        self.assertTrue(c.okay())
        c = doImport("import_test.two.three.success.okay")
        self.assertTrue(c())
        c = doImport("import_test.two.three.success.Container")
        self.assertEqual(c.inside(), "1")
        c = doImport("import_test.two.three.success.Container.inside")
        self.assertEqual(c(), "1")

    def testDoImportType(self):
        with self.assertRaises(TypeError):
            doImportType("lsst.utils")

        c = doImportType("lsst.utils.tests.TestCase")
        self.assertEqual(c, lsst.utils.tests.TestCase)


if __name__ == "__main__":
    unittest.main()
