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

import unittest

from astropy import units as u
from lsst.utils.usage import get_current_mem_usage, get_peak_mem_usage


class UsageTestCase(unittest.TestCase):
    def testGetCurrentMemUsage(self):
        main, children = get_current_mem_usage()
        self.assertGreater(main, 0 * u.byte)
        self.assertGreaterEqual(children, 0 * u.byte)

        self.assertTrue(main.unit.is_equivalent(u.byte))
        self.assertTrue(children.unit.is_equivalent(u.byte))

    def testGetPeakMemUsage(self):
        main, child = get_peak_mem_usage()
        self.assertGreater(main, 0 * u.byte)
        self.assertGreaterEqual(child, 0 * u.byte)

        self.assertTrue(main.unit.is_equivalent(u.byte))
        self.assertTrue(child.unit.is_equivalent(u.byte))


if __name__ == "__main__":
    unittest.main()
