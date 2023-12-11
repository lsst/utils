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

import os
import unittest

import lsst.utils.tests


class ExplicitBinaryTester(lsst.utils.tests.ExecutablesTestCase):
    """Test that a named executable can be run."""

    def testSimpleExe(self):
        """Test explicit shell script."""
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
    """Run test binaries in this package."""


EXECUTABLES = None
UtilsBinaryTester.create_executable_tests(__file__, EXECUTABLES)

if __name__ == "__main__":
    unittest.main()
