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

import sys
import unittest

import lsst.utils.tests
import numpy as np

# set to True to test plotting and printing by-eye when tests fail
display = False


class UtilsTestCase(lsst.utils.tests.TestCase):
    """Test the utils test case."""

    def setUp(self):
        self.large = 100.0
        self.epsilon = 1e-8
        self.zeros = np.zeros((5, 5), dtype=float)
        self.zeros2 = np.zeros((5, 5), dtype=float)
        self.epsilons = np.zeros((5, 5), dtype=float) + self.epsilon
        self.larges = np.zeros((5, 5), dtype=float) + self.large
        self.larges2 = np.zeros((5, 5), dtype=float) + self.large
        self.largesOneOff = self.larges.copy()
        self.largesOneOff[0] += self.epsilon
        self.largesEpsilon = np.zeros((5, 5), dtype=float) + self.large + self.epsilon
        self.ranges = np.arange(-12.0, 13.0).reshape(5, 5)
        self.rangesEpsilon = self.ranges.copy()
        self.rangesEpsilon += np.linspace(-1e-4, 1e-4, 5)

    def test_assertFloatsAlmostEqual(self):
        # zero scalar tests
        self.assertFloatsAlmostEqual(0.0, 0.0)
        self.assertFloatsAlmostEqual(0.0, 1e-8, atol=1e-7)
        self.assertFloatsAlmostEqual(0.0, 1e-8, atol=1e-7, rtol=None)
        self.assertFloatsAlmostEqual(0.0, 1e-8, atol=None, rtol=1e-5, relTo=1e-2)

        # zero array vs. scalar tests
        self.assertFloatsAlmostEqual(self.zeros, 0.0)
        self.assertFloatsAlmostEqual(self.zeros, self.epsilon, atol=1e-7)
        self.assertFloatsAlmostEqual(self.zeros, self.epsilon, atol=1e-7, rtol=None)
        self.assertFloatsAlmostEqual(self.zeros, self.epsilon, atol=None, rtol=1e-5, relTo=1e-2)

        # zero array vs. array tests
        self.assertFloatsAlmostEqual(self.zeros, self.zeros2)
        self.assertFloatsAlmostEqual(self.zeros, self.zeros2, rtol=None)
        self.assertFloatsAlmostEqual(self.zeros, self.zeros2, atol=None)
        self.assertFloatsAlmostEqual(self.zeros, self.epsilons, atol=1e-7)
        self.assertFloatsAlmostEqual(self.zeros, self.epsilons, atol=1e-7, rtol=None)
        self.assertFloatsAlmostEqual(self.zeros, self.epsilons, atol=None, rtol=1e-5, relTo=1e-2)

        # invalid value tests
        with self.assertRaises(ValueError):
            self.assertFloatsAlmostEqual(self.zeros, self.zeros2, atol=None, rtol=None)

        # non-zero scalar tests
        self.assertFloatsAlmostEqual(self.large, 100.0)
        self.assertFloatsAlmostEqual(self.large, self.large + self.epsilon, rtol=1e-7)
        self.assertFloatsAlmostEqual(self.large, self.large + self.epsilon, rtol=1e-7, atol=None)
        self.assertFloatsAlmostEqual(self.large, self.large + self.epsilon, rtol=1e-7, relTo=100.0)

        # Non-zero array vs. scalar tests
        self.assertFloatsAlmostEqual(self.larges, self.large)
        self.assertFloatsAlmostEqual(self.larges, self.large + self.epsilon, rtol=1e-7)
        self.assertFloatsAlmostEqual(self.larges, self.large + self.epsilon, rtol=1e-7, atol=None)
        self.assertFloatsAlmostEqual(self.larges, self.large + self.epsilon, rtol=1e-7, relTo=100.0)

        # Non-zero array vs. array tests
        self.assertFloatsAlmostEqual(self.larges, self.larges2)
        self.assertFloatsAlmostEqual(self.larges, self.largesEpsilon, rtol=1e-7)
        self.assertFloatsAlmostEqual(self.larges, self.largesEpsilon, rtol=1e-7, atol=None)
        self.assertFloatsAlmostEqual(self.larges, self.largesEpsilon, rtol=1e-7, relTo=100.0)
        self.assertFloatsAlmostEqual(self.larges, self.largesOneOff, atol=1e-7)
        self.assertFloatsAlmostEqual(self.ranges, self.rangesEpsilon, rtol=1e-3, atol=1e-4)

        # Test that it raises appropriately
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.large, 0.0)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.large, 0.0, rtol=1e-2)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.large, 0.0, rtol=1e-2, atol=None)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.large, 0.0, atol=1e-2)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.large, 0.0, atol=1e-2, rtol=None)

        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, 0.0)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, 0.0, rtol=1e-2)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, 0.0, rtol=1e-2, atol=None)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, 0.0, atol=1e-2)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, 0.0, atol=1e-2, rtol=None)

        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(0.0, self.larges)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(0.0, self.larges, rtol=1e-2)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(0.0, self.larges, rtol=1e-2, atol=None)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(0.0, self.larges, atol=1e-2)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(0.0, self.larges, atol=1e-2, rtol=None)

        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, self.largesEpsilon, rtol=1e-16)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, self.largesEpsilon, rtol=1e-16, atol=None)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, self.largesEpsilon, rtol=1e-16, relTo=100.0)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, self.largesOneOff, atol=1e-16)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, self.largesOneOff, atol=1e-16, rtol=None)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.ranges, self.rangesEpsilon, rtol=1e-15, atol=1e-4)

        if display:
            # should see failures on the center row of the 5x5 image, but not
            # the very center point.
            nonzeroCenter = self.zeros.copy()
            nonzeroCenter[2, :] = 1e-5
            with self.assertRaises(AssertionError):
                self.assertFloatsAlmostEqual(self.zeros, nonzeroCenter, rtol=1e-6, plotOnFailure=True)

        with self.assertRaises(AssertionError) as cm:
            self.assertFloatsAlmostEqual(10, 0, msg="This is an error message.")
        self.assertIn("This is an error message.", str(cm.exception))
        self.assertIn("10 != 0; diff=10/10=1.0 with rtol=", str(cm.exception))

    def test_assertFloatsNotEqual(self):
        # zero scalar tests
        self.assertFloatsNotEqual(0.0, 1.0)
        self.assertFloatsNotEqual(0.0, 1e-8, atol=1e-9)
        self.assertFloatsNotEqual(0.0, 1e-8, atol=1e-9, rtol=None)
        self.assertFloatsNotEqual(0.0, 1e-8, atol=None, rtol=1e-7, relTo=1e-2)

        # zero array vs. scalar tests
        self.assertFloatsNotEqual(self.zeros, 1.0)
        self.assertFloatsNotEqual(self.zeros, self.epsilon, atol=1e-9)
        self.assertFloatsNotEqual(self.zeros, self.epsilon, atol=1e-9, rtol=None)
        self.assertFloatsNotEqual(self.zeros, self.epsilon, atol=None, rtol=1e-7, relTo=1e-2)

        # zero array vs. array tests
        self.assertFloatsNotEqual(self.zeros, self.larges)
        self.assertFloatsNotEqual(self.zeros, self.epsilon, atol=1e-9, rtol=None)
        self.assertFloatsNotEqual(self.zeros, self.epsilon, atol=None, rtol=1e-5, relTo=1e-5)
        self.assertFloatsNotEqual(self.zeros, self.epsilons, atol=1e-9)
        self.assertFloatsNotEqual(self.zeros, self.epsilons, atol=1e-9, rtol=None)
        self.assertFloatsNotEqual(self.zeros, self.epsilons, atol=None, rtol=1e-7, relTo=1e-2)

        # invalid value tests
        with self.assertRaises(ValueError):
            self.assertFloatsNotEqual(self.zeros, self.zeros2, atol=None, rtol=None)

        # non-zero scalar tests
        self.assertFloatsNotEqual(self.large, 1.0)
        self.assertFloatsNotEqual(self.large, self.large + self.epsilon, atol=1e-9)
        self.assertFloatsNotEqual(self.large, self.large + self.epsilon, rtol=1e-11, atol=None)
        self.assertFloatsNotEqual(self.large, self.large + self.epsilon, rtol=1e-12, relTo=1.0)

        # Non-zero array vs. scalar tests
        self.assertFloatsNotEqual(self.larges, self.large + self.epsilon, atol=1e-9)
        self.assertFloatsNotEqual(self.larges, self.large + self.epsilon, atol=1e-9, rtol=None)
        self.assertFloatsNotEqual(self.larges, self.large + self.epsilon, rtol=1e-11, atol=None)
        self.assertFloatsNotEqual(self.larges, self.large + self.epsilon, rtol=1e-12, relTo=1.0)

        # Non-zero array vs. array tests
        self.assertFloatsNotEqual(self.larges, self.zeros)
        self.assertFloatsNotEqual(self.larges, self.largesEpsilon, rtol=1e-12)
        self.assertFloatsNotEqual(self.larges, self.largesEpsilon, rtol=1e-12, atol=None)
        self.assertFloatsNotEqual(self.larges, self.largesEpsilon, rtol=1e-11, relTo=100.0)
        self.assertFloatsNotEqual(self.larges, self.largesOneOff, atol=1e-9)
        self.assertFloatsNotEqual(self.larges, self.largesOneOff, atol=1e-9, rtol=None)
        self.assertFloatsNotEqual(self.ranges, self.rangesEpsilon)

        with self.assertRaises(AssertionError) as cm:
            self.assertFloatsNotEqual(10, 10, msg="This is an error message.")
        self.assertIn("This is an error message.", str(cm.exception))
        self.assertIn("10 == 10; diff=0/10=0.0 with rtol=", str(cm.exception))

    def test_assertFloatsEqual(self):
        self.assertFloatsEqual(0, 0)
        self.assertFloatsEqual(0.0, 0.0)
        self.assertFloatsEqual(1, 1)
        self.assertFloatsEqual(1.0, 1.0)
        self.assertFloatsEqual(self.zeros, self.zeros2)
        self.assertFloatsEqual(self.zeros, 0)
        self.assertFloatsEqual(self.zeros, 0.0)
        self.assertFloatsEqual(self.larges, self.large)
        with self.assertRaises(AssertionError):
            self.assertFloatsEqual(self.larges, 0.0)
        with self.assertRaises(AssertionError):
            self.assertFloatsEqual(self.larges, self.largesEpsilon)
        with self.assertRaises(AssertionError):
            self.assertFloatsEqual(self.larges, self.zeros)
        with self.assertRaises(AssertionError):
            self.assertFloatsEqual(self.larges, self.largesEpsilon)

    def test_notfinite(self):
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(np.nan, 0.0)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(0.0, np.inf)
        self.assertFloatsEqual(np.nan, np.nan, ignoreNaNs=True)
        self.assertFloatsEqual(np.nan, np.array([np.nan, np.nan]), ignoreNaNs=True)
        self.assertFloatsEqual(np.array([np.nan, np.nan]), np.nan, ignoreNaNs=True)
        self.assertFloatsEqual(np.array([np.nan, np.nan]), np.array([np.nan, np.nan]), ignoreNaNs=True)
        self.assertFloatsEqual(np.array([np.nan, 0.5]), np.array([np.nan, 0.5]), ignoreNaNs=True)
        self.assertFloatsEqual(0.5, np.array([0.5, 0.5]), ignoreNaNs=True)
        self.assertFloatsEqual(np.array([0.5, 0.5]), 0.5, ignoreNaNs=True)
        with self.assertRaises(AssertionError):
            self.assertFloatsEqual(np.array([np.nan, 0.5]), np.array([0.5, np.nan]), ignoreNaNs=True)
        with self.assertRaises(AssertionError):
            self.assertFloatsEqual(0.5, np.array([0.5, np.nan]), ignoreNaNs=True)
        with self.assertRaises(AssertionError):
            self.assertFloatsEqual(np.nan, np.array([0.5, np.nan]), ignoreNaNs=True)
        with self.assertRaises(AssertionError):
            self.assertFloatsEqual(np.array([0.5, np.nan]), 0.5, ignoreNaNs=True)
        with self.assertRaises(AssertionError):
            self.assertFloatsEqual(np.array([0.5, np.nan]), np.nan, ignoreNaNs=True)
        with self.assertRaises(AssertionError):
            self.assertFloatsEqual(np.array([np.nan, 1.0]), np.array([np.nan, 0.5]), ignoreNaNs=True)


class TestMemory(lsst.utils.tests.MemoryTestCase):
    """Test for file descriptor leaks.

    Verify that setting ignore_regexps doesn't cause anything to fail.
    """

    ignore_regexps = [r"\.extension$"]


def setup_module(module):
    """Initialize the pytest environment."""
    lsst.utils.tests.init()


if __name__ == "__main__":
    setup_module(sys.modules[__name__])
    unittest.main()
