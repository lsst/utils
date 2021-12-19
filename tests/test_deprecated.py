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


class DeprecatedTestCase(lsst.utils.tests.TestCase):
    def test_deprecate_pybind11(self):
        def old(x):
            """Docstring"""
            return x + 1

        # Use an unusual category
        old = lsst.utils.deprecate_pybind11(
            old, reason="For testing.", version="unknown", category=PendingDeprecationWarning
        )
        with self.assertWarnsRegex(
            PendingDeprecationWarning,
            r"Call to deprecated function \(or staticmethod\) old\. \(For testing\.\) "
            "-- Deprecated since version unknown.$",
        ):
            # Check that the function still works
            self.assertEqual(old(3), 4)
        self.assertIn("Docstring", old.__doc__)
        self.assertIn("For testing.", old.__doc__)


if __name__ == "__main__":
    unittest.main()
