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

import unittest

from lsst.utils.tests import ImportTestCase


class TestImports(ImportTestCase):
    """Test we can run the import tests.

    All the code in utils is being tested and imported already but this
    will confirm the test infrastructure works.
    """

    PACKAGES = ("lsst.utils",)

    def test_counter(self):
        """Test that the expected number of packages were registered."""
        self.assertEqual(self._n_registered, 1)


class TestSkipImports(ImportTestCase):
    """Test that we can run the import tests with some modules skipped."""

    PACKAGES = ("import_test.two.three",)
    SKIP_FILES = {"import_test.two.three": {"runtime.py", "fail.py"}}

    def test_import(self):
        """Test that we can import utils."""
        import import_test  # noqa: F401


if __name__ == "__main__":
    unittest.main()
