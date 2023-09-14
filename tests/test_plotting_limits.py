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

import numpy as np
from lsst.utils.plotting.limits import calculate_safe_plotting_limits, make_calculate_safe_plotting_limits


class PlottingLimitsClosureTestCase(unittest.TestCase):
    """Tests for `make_calculate_safe_plotting_limits` function."""

    xs = np.linspace(0, 10, 10000)
    series1 = np.sin(xs + 3.1415 / 2) + 0.75  # min=-0.24999, max=1.74999
    series1_min = min(series1)
    series1_max = max(series1)

    series2 = np.sin(xs) + 1.2  # min=0.2, max=2.19999
    series2_min = min(series2)
    series2_max = max(series2)

    outliers = series1[:]
    outliers[1000] = 20
    outliers[2000] = -1000

    def testSingleSeries(self):
        """Test that a single series works and the outliers exclusion works."""
        # Deliberately test the bounds are the same when using the series
        # itself, and the copy with the outlier values, i.e. using
        # self.series1_min/max inside the loop despite changing the series we
        # loop over is the intent here, not a bug.
        for series in [self.series1, self.outliers]:
            ymin, ymax = make_calculate_safe_plotting_limits()(series)
            self.assertLess(ymin, self.series1_min)
            self.assertGreater(ymin, self.series1_min - 1)
            self.assertLess(ymax, self.series1_max + 1)
            self.assertGreater(ymax, self.series1_max)

    def testMultipleSeries(self):
        """Test that passing multiple several series in works wrt outliers."""
        calculate_safe_plotting_limits_accumulator = make_calculate_safe_plotting_limits()
        _, _ = calculate_safe_plotting_limits_accumulator(self.series1)
        ymin, ymax = calculate_safe_plotting_limits_accumulator(self.outliers)

        self.assertLess(ymin, self.series1_min)
        self.assertGreater(ymin, self.series1_min - 1)
        self.assertLess(ymax, self.series1_max + 1)
        self.assertGreater(ymax, self.series1_max)

    def testMultipleSeriesCommonRange(self):
        """Test that passing multiple several series in works wrt outliers."""
        calculate_safe_plotting_limits_accumulator = make_calculate_safe_plotting_limits()
        _, _ = calculate_safe_plotting_limits_accumulator(self.series1)
        ymin, ymax = calculate_safe_plotting_limits_accumulator(self.series2)
        # lower bound less than the lowest of the two
        self.assertLess(ymin, min(self.series1_min, self.series2_min))
        # lower bound less than the lowest of the two, but not by much
        self.assertGreater(ymin, min(self.series1_min, self.series2_min) - 1)
        # upper bound greater than the highest of the two
        self.assertGreater(ymax, max(self.series1_max, self.series2_max))
        # upper bound greater than the highest of the two, but not by much
        self.assertLess(ymax, max(self.series1_max, self.series2_max) + 1)

    def testSymmetric(self):
        """Test that the symmetric option works"""
        calc = make_calculate_safe_plotting_limits(symmetric_around_zero=True)
        _, _ = calc(self.series1)
        ymin, ymax = calc(self.outliers)

        self.assertEqual(ymin, -ymax)
        self.assertGreater(ymax, self.series1_max)
        self.assertLess(ymin, self.series1_min)

    def testConstantExtra(self):
        """Test that the constantExtra option works"""
        calc = make_calculate_safe_plotting_limits(constant_extra=0)
        _, _ = calc(self.series1)
        strictMin, strictMax = calc(self.outliers)

        self.assertAlmostEqual(strictMin, self.series1_min, places=4)
        self.assertAlmostEqual(strictMax, self.series1_max, places=4)

        for extra in [-2.123, -1, 0, 1, 1.5, 23]:
            calc = make_calculate_safe_plotting_limits(constant_extra=extra)
            _, _ = calc(self.series1)
            ymin, ymax = calc(self.outliers)

            self.assertAlmostEqual(ymin, self.series1_min - extra, places=4)
            self.assertAlmostEqual(ymax, self.series1_max + extra, places=4)

    def testSeriesOfSeries(self):
        """Test that we can pass a list of series to the accumulator in one."""
        calculate_safe_plotting_limits_accumulator = make_calculate_safe_plotting_limits()
        ymin, ymax = calculate_safe_plotting_limits_accumulator([self.series1, self.outliers])

        self.assertLess(ymin, self.series1_min)
        self.assertGreater(ymin, self.series1_min - 1)
        self.assertLess(ymax, self.series1_max + 1)
        self.assertGreater(ymax, self.series1_max)

    def testRaises(self):
        with self.assertRaises(TypeError):
            make_calculate_safe_plotting_limits()(1.234)


class PlottingLimitsTestCase(unittest.TestCase):
    """Tests for `calculate_safe_plotting_limits` function."""

    xs = np.linspace(0, 10, 10000)
    series1 = np.sin(xs + 3.1415 / 2) + 0.75  # min=-0.24999, max=1.74999
    series1_min = min(series1)
    series1_max = max(series1)

    series2 = np.sin(xs) + 1.2  # min=0.2, max=2.19999
    series2_min = min(series2)
    series2_max = max(series2)

    outliers = series1[:]
    outliers[1000] = 20
    outliers[2000] = -1000

    def testSingleSeries(self):
        """Test that a single series works and the outliers exclusion works."""
        # Deliberately test the bounds are the same when using the series
        # itself, and the copy with the outlier values, i.e. using
        # self.series1_min/max inside the loop despite changing the series we
        # loop over is the intent here, not a bug.
        for series in [self.series1, self.outliers]:
            ymin, ymax = calculate_safe_plotting_limits(series)
            self.assertLess(ymin, self.series1_min)
            self.assertGreater(ymin, self.series1_min - 1)
            self.assertLess(ymax, self.series1_max + 1)
            self.assertGreater(ymax, self.series1_max)

    def testMultipleSeries(self):
        """Test that passing multiple several series in works wrt outliers."""
        ymin, ymax = calculate_safe_plotting_limits([self.series1, self.outliers])
        self.assertLess(ymin, self.series1_min)
        self.assertGreater(ymin, self.series1_min - 1)
        self.assertLess(ymax, self.series1_max + 1)
        self.assertGreater(ymax, self.series1_max)

    def testMultipleSeriesCommonRange(self):
        """Test that passing multiple several series in works wrt outliers."""
        ymin, ymax = calculate_safe_plotting_limits([self.series1, self.series2])
        # lower bound less than the lowest of the two
        self.assertLess(ymin, min(self.series1_min, self.series2_min))
        # lower bound less than the lowest of the two, but not by much
        self.assertGreater(ymin, min(self.series1_min, self.series2_min) - 1)
        # upper bound greater than the highest of the two
        self.assertGreater(ymax, max(self.series1_max, self.series2_max))
        # upper bound greater than the highest of the two, but not by much
        self.assertLess(ymax, max(self.series1_max, self.series2_max) + 1)

    def testSymmetric(self):
        """Test that the symmetric option works"""
        ymin, ymax = calculate_safe_plotting_limits([self.series1, self.outliers], symmetric_around_zero=True)
        self.assertEqual(ymin, -ymax)
        self.assertGreater(ymax, self.series1_max)
        self.assertLess(ymin, self.series1_min)

    def testConstantExtra(self):
        """Test that the constantExtra option works"""
        strictMin, strictMax = calculate_safe_plotting_limits([self.series1, self.outliers], constant_extra=0)
        self.assertAlmostEqual(strictMin, self.series1_min, places=4)
        self.assertAlmostEqual(strictMax, self.series1_max, places=4)

        for extra in [-2.123, -1, 0, 1, 1.5, 23]:
            ymin, ymax = calculate_safe_plotting_limits([self.series1, self.outliers], constant_extra=extra)
            self.assertAlmostEqual(ymin, self.series1_min - extra, places=4)
            self.assertAlmostEqual(ymax, self.series1_max + extra, places=4)

    def testRaises(self):
        with self.assertRaises(TypeError):
            calculate_safe_plotting_limits(1.234)


if __name__ == "__main__":
    unittest.main()
