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

import lsst.utils
import lsst.utils.tests
from lsst.utils.ellipsis import Ellipsis, EllipsisType


class EllipsisTestCase(lsst.utils.tests.TestCase):
    """Test ellipsis handling."""

    def test_ellipsis(self):
        # These are true at runtime because of typing.TYPE_CHECKING guards in
        # the module.  When MyPy or other type-checkers run, these assertions
        # would not be true, and `Ellipsis` must be used instead of the literal
        # `...` to be understood by mypy.
        self.assertIs(Ellipsis, ...)
        self.assertIs(EllipsisType, type(...))


if __name__ == "__main__":
    unittest.main()
