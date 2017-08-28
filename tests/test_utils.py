#
# LSST Data Management System
# Copyright 2008-2016 LSST Corporation.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
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
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <http://www.lsstcorp.org/LegalNotices/>.
#
import sys
import unittest
import numpy as np

import lsst.utils.tests

# set to True to test plotting and printing by-eye when tests fail
display = False


class UtilsTestCase(lsst.utils.tests.TestCase):
    def setUp(self):
        self.large = 100.
        self.epsilon = 1e-8
        self.zeros = np.zeros((5, 5), dtype=float)
        self.zeros2 = np.zeros((5, 5), dtype=float)
        self.epsilons = np.zeros((5, 5), dtype=float) + self.epsilon
        self.larges = np.zeros((5, 5), dtype=float) + self.large
        self.larges2 = np.zeros((5, 5), dtype=float) + self.large
        self.largesOneOff = self.larges.copy()
        self.largesOneOff[0] += self.epsilon
        self.largesEpsilon = np.zeros((5, 5), dtype=float) + self.large + self.epsilon
        self.ranges = np.arange(-12., 13.).reshape(5, 5)
        self.rangesEpsilon = self.ranges.copy()
        self.rangesEpsilon += np.linspace(-1E-4, 1E-4, 5)

    def test_assertFloatsAlmostEqual(self):
        # zero scalar tests
        self.assertFloatsAlmostEqual(0.0, 0.0)
        self.assertFloatsAlmostEqual(0.0, 1E-8, atol=1E-7)
        self.assertFloatsAlmostEqual(0.0, 1E-8, atol=1E-7, rtol=None)
        self.assertFloatsAlmostEqual(0.0, 1E-8, atol=None, rtol=1E-5, relTo=1E-2)

        # zero array vs. scalar tests
        self.assertFloatsAlmostEqual(self.zeros, 0.)
        self.assertFloatsAlmostEqual(self.zeros, self.epsilon, atol=1E-7)
        self.assertFloatsAlmostEqual(self.zeros, self.epsilon, atol=1E-7, rtol=None)
        self.assertFloatsAlmostEqual(self.zeros, self.epsilon, atol=None, rtol=1E-5, relTo=1E-2)

        # zero array vs. array tests
        self.assertFloatsAlmostEqual(self.zeros, self.zeros2)
        self.assertFloatsAlmostEqual(self.zeros, self.zeros2, rtol=None)
        self.assertFloatsAlmostEqual(self.zeros, self.zeros2, atol=None)
        self.assertFloatsAlmostEqual(self.zeros, self.epsilons, atol=1E-7)
        self.assertFloatsAlmostEqual(self.zeros, self.epsilons, atol=1E-7, rtol=None)
        self.assertFloatsAlmostEqual(self.zeros, self.epsilons, atol=None, rtol=1E-5, relTo=1E-2)

        # invalid value tests
        with self.assertRaises(ValueError):
            self.assertFloatsAlmostEqual(self.zeros, self.zeros2, atol=None, rtol=None)

        # non-zero scalar tests
        self.assertFloatsAlmostEqual(self.large, 100.)
        self.assertFloatsAlmostEqual(self.large, self.large + self.epsilon, rtol=1E-7)
        self.assertFloatsAlmostEqual(self.large, self.large + self.epsilon, rtol=1E-7, atol=None)
        self.assertFloatsAlmostEqual(self.large, self.large + self.epsilon, rtol=1E-7, relTo=100.0)

        # Non-zero array vs. scalar tests
        self.assertFloatsAlmostEqual(self.larges, self.large)
        self.assertFloatsAlmostEqual(self.larges, self.large + self.epsilon, rtol=1E-7)
        self.assertFloatsAlmostEqual(self.larges, self.large + self.epsilon, rtol=1E-7, atol=None)
        self.assertFloatsAlmostEqual(self.larges, self.large + self.epsilon, rtol=1E-7, relTo=100.0)

        # Non-zero array vs. array tests
        self.assertFloatsAlmostEqual(self.larges, self.larges2)
        self.assertFloatsAlmostEqual(self.larges, self.largesEpsilon, rtol=1E-7)
        self.assertFloatsAlmostEqual(self.larges, self.largesEpsilon, rtol=1E-7, atol=None)
        self.assertFloatsAlmostEqual(self.larges, self.largesEpsilon, rtol=1E-7, relTo=100.0)
        self.assertFloatsAlmostEqual(self.larges, self.largesOneOff, atol=1e-7)
        self.assertFloatsAlmostEqual(self.ranges, self.rangesEpsilon, rtol=1E-3, atol=1E-4)

        # Test that it raises appropriately
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.large, 0.)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.large, 0., rtol=1E-2)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.large, 0., rtol=1E-2, atol=None)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.large, 0., atol=1e-2)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.large, 0., atol=1e-2, rtol=None)

        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, 0.)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, 0., rtol=1E-2)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, 0., rtol=1E-2, atol=None)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, 0., atol=1e-2)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, 0., atol=1e-2, rtol=None)

        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(0., self.larges)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(0., self.larges, rtol=1E-2)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(0., self.larges, rtol=1E-2, atol=None)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(0., self.larges, atol=1e-2)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(0., self.larges, atol=1e-2, rtol=None)

        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, self.largesEpsilon, rtol=1E-16)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, self.largesEpsilon, rtol=1E-16, atol=None)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, self.largesEpsilon, rtol=1E-16, relTo=100.0)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, self.largesOneOff, atol=1e-16)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.larges, self.largesOneOff, atol=1e-16, rtol=None)
        with self.assertRaises(AssertionError):
            self.assertFloatsAlmostEqual(self.ranges, self.rangesEpsilon, rtol=1E-15, atol=1E-4)

        if display:
            # should see failures on the center row of the 5x5 image, but not the very center point
            nonzeroCenter = self.zeros.copy()
            nonzeroCenter[2, :] = 1e-5
            with self.assertRaises(AssertionError):
                self.assertFloatsAlmostEqual(self.zeros, nonzeroCenter, rtol=1E-6, plotOnFailure=True)

        with self.assertRaises(AssertionError) as cm:
            self.assertFloatsAlmostEqual(10, 0, msg="This is an error message.")
        self.assertIn("This is an error message.", str(cm.exception))
        self.assertIn("10 != 0; diff=10/10=1.0 with rtol=", str(cm.exception))

    def test_assertFloatsNotEqual(self):
        # zero scalar tests
        self.assertFloatsNotEqual(0.0, 1.0)
        self.assertFloatsNotEqual(0.0, 1E-8, atol=1E-9)
        self.assertFloatsNotEqual(0.0, 1E-8, atol=1E-9, rtol=None)
        self.assertFloatsNotEqual(0.0, 1E-8, atol=None, rtol=1E-7, relTo=1E-2)

        # zero array vs. scalar tests
        self.assertFloatsNotEqual(self.zeros, 1.)
        self.assertFloatsNotEqual(self.zeros, self.epsilon, atol=1E-9)
        self.assertFloatsNotEqual(self.zeros, self.epsilon, atol=1E-9, rtol=None)
        self.assertFloatsNotEqual(self.zeros, self.epsilon, atol=None, rtol=1E-7, relTo=1E-2)

        # zero array vs. array tests
        self.assertFloatsNotEqual(self.zeros, self.larges)
        self.assertFloatsNotEqual(self.zeros, self.epsilon, atol=1E-9, rtol=None)
        self.assertFloatsNotEqual(self.zeros, self.epsilon, atol=None, rtol=1e-5, relTo=1e-5)
        self.assertFloatsNotEqual(self.zeros, self.epsilons, atol=1E-9)
        self.assertFloatsNotEqual(self.zeros, self.epsilons, atol=1E-9, rtol=None)
        self.assertFloatsNotEqual(self.zeros, self.epsilons, atol=None, rtol=1E-7, relTo=1E-2)

        # invalid value tests
        with self.assertRaises(ValueError):
            self.assertFloatsNotEqual(self.zeros, self.zeros2, atol=None, rtol=None)

        # non-zero scalar tests
        self.assertFloatsNotEqual(self.large, 1.)
        self.assertFloatsNotEqual(self.large, self.large + self.epsilon, atol=1E-9)
        self.assertFloatsNotEqual(self.large, self.large + self.epsilon, rtol=1E-11, atol=None)
        self.assertFloatsNotEqual(self.large, self.large + self.epsilon, rtol=1E-12, relTo=1.)

        # Non-zero array vs. scalar tests
        self.assertFloatsNotEqual(self.larges, self.large + self.epsilon, atol=1e-9)
        self.assertFloatsNotEqual(self.larges, self.large + self.epsilon, atol=1e-9, rtol=None)
        self.assertFloatsNotEqual(self.larges, self.large + self.epsilon, rtol=1E-11, atol=None)
        self.assertFloatsNotEqual(self.larges, self.large + self.epsilon, rtol=1E-12, relTo=1.)

        # Non-zero array vs. array tests
        self.assertFloatsNotEqual(self.larges, self.zeros)
        self.assertFloatsNotEqual(self.larges, self.largesEpsilon, rtol=1E-12)
        self.assertFloatsNotEqual(self.larges, self.largesEpsilon, rtol=1E-12, atol=None)
        self.assertFloatsNotEqual(self.larges, self.largesEpsilon, rtol=1E-11, relTo=100.0)
        self.assertFloatsNotEqual(self.larges, self.largesOneOff, atol=1e-9)
        self.assertFloatsNotEqual(self.larges, self.largesOneOff, atol=1e-9, rtol=None)
        self.assertFloatsNotEqual(self.ranges, self.rangesEpsilon)

        with self.assertRaises(AssertionError) as cm:
            self.assertFloatsNotEqual(10, 10, msg="This is an error message.")
        self.assertIn("This is an error message.", str(cm.exception))
        self.assertIn("10 == 10; diff=0/10=0.0 with rtol=", str(cm.exception))

    def test_assertFloatsEqual(self):
        self.assertFloatsEqual(0, 0)
        self.assertFloatsEqual(0., 0.)
        self.assertFloatsEqual(1, 1)
        self.assertFloatsEqual(1., 1.)
        self.assertFloatsEqual(self.zeros, self.zeros2)
        self.assertFloatsEqual(self.zeros, 0)
        self.assertFloatsEqual(self.zeros, 0.)
        self.assertFloatsEqual(self.larges, self.large)
        with self.assertRaises(AssertionError):
            self.assertFloatsEqual(self.larges, 0.)
        with self.assertRaises(AssertionError):
            self.assertFloatsEqual(self.larges, self.largesEpsilon)
        with self.assertRaises(AssertionError):
            self.assertFloatsEqual(self.larges, self.zeros)
        with self.assertRaises(AssertionError):
            self.assertFloatsEqual(self.larges, self.largesEpsilon)


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    setup_module(sys.modules[__name__])
    unittest.main()
