# This file is part of utils.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# Use of this source code is governed by a 3-clause BSD-style
# license that can be found in the LICENSE file.

import unittest

from lsst.utils.tests import ImportTestCase


class TestImports(ImportTestCase):
    """Test we can run the import tests.

    All the code in utils is being tested and imported already but this
    will confirm the test infrastructure works.
    """

    PACKAGES = ("lsst.utils",)

    def test_counter(self):
        """Test that the expected number of packages were registered."""
        self.assertEqual(self._n_registered, 1)


if __name__ == "__main__":
    unittest.main()
