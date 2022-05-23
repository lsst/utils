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

import lsst.utils
import lsst.utils.tests
from lsst.utils.ellipsis import Ellipsis, EllipsisType


class EllipsisTestCase(lsst.utils.tests.TestCase):
    def test_ellipsis(self):
        # These are true at runtime because of typing.TYPE_CHECKING guards in
        # the module.  When MyPy or other type-checkers run, these assertions
        # would not be true, and `Ellipsis` must be used instead of the literal
        # `...` to be understood by mypy.
        self.assertIs(Ellipsis, ...)
        self.assertIs(EllipsisType, type(...))


if __name__ == "__main__":
    unittest.main()
