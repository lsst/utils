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
        main1, children1 = get_current_mem_usage()
        self.assertGreater(main1, 0 * u.byte)
        self.assertGreaterEqual(children1.value, 0)

        self.assertTrue(main1.unit.is_equivalent(u.byte))
        self.assertTrue(children1.unit.is_equivalent(u.byte))

        # Allocate some memory.
        arr = [None] * 1_000_000  # noqa: F841

        main2, children2 = get_current_mem_usage()
        self.assertGreater(main2, main1)
        self.assertGreaterEqual(children2, children1)

    def testGetPeakMemUsage(self):
        main1, child1 = get_peak_mem_usage()
        self.assertGreater(main1, 0 * u.byte)
        self.assertGreaterEqual(child1, 0 * u.byte)

        self.assertTrue(main1.unit.is_equivalent(u.byte))
        self.assertTrue(child1.unit.is_equivalent(u.byte))

        # Allocate some memory.
        arr = [None] * 2_000_000  # noqa: F841

        main2, child2 = get_peak_mem_usage()
        self.assertGreater(main2, main1)
        self.assertGreaterEqual(child2, child1)


if __name__ == "__main__":
    unittest.main()
