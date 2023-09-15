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

from astropy import units as u
from lsst.utils.usage import get_current_mem_usage, get_peak_mem_usage


class UsageTestCase(unittest.TestCase):
    """Test resource usage functions."""

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
