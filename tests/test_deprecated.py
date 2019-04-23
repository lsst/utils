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

import unittest
import lsst.utils.tests

import lsst.utils


class DeprecatedTestCase(lsst.utils.tests.TestCase):
    def test_deprecate_pybind11(self):
        def old(x):
            """Docstring"""
            return x + 1
        # Use an unusual category
        old = lsst.utils.deprecate_pybind11(
            old, reason="For testing.", category=PendingDeprecationWarning)
        with self.assertWarnsRegex(
                PendingDeprecationWarning,
                r"Call to deprecated function \(or staticmethod\) old\. \(For testing\.\)$"):
            # Check that the function still works
            self.assertEqual(old(3), 4)
        self.assertIn("Docstring", old.__doc__)
        self.assertIn("For testing.", old.__doc__)


if __name__ == "__main__":
    unittest.main()
